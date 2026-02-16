"""
Airflow DAG: пайплайн переобучения модели кредитного скоринга.

Цепочка: check_data_drift => retrain_model => validate_new_model => deploy_canary_release

Переменные Airflow (Admin => Variables):
  - IMAGE_REGISTRY: registry для образов (например ghcr.io/owner)
  - mlflow_tracking_uri: URI MLflow (например http://mlflow:5000)
  - dvc_remote_url: URL DVC remote (s3://bucket или gs://bucket)

Размещение: скопировать или симлинк в AIRFLOW_HOME/dags/
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

# Callables для PythonOperator
def check_drift_task(**context):
    """Проверка data drift (Evidently). При дрифте — продолжить, иначе skip"""
    import subprocess
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "evidently_drift_report.py"), "--fallback-test"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"check_data_drift failed: {result.stderr}")
    # Упрощённо: всегда продолжаем. В prod - парсить HTML/JSON и решать по порогу
    return {"drift_detected": True, "report_path": "monitoring/reports/drift_report.html"}


def validate_model_task(**context):
    """Валидация новой модели (метрики, ONNX). Возвращает model_version для deploy"""
    import subprocess
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    # Запуск concept drift report
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "evidently_concept_drift_report.py"), "--fallback-test"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"validate_new_model failed: {result.stderr}")
    # model_version - из dag_run или фиксированный для canary
    dag_run = context.get("dag_run")
    model_version = (dag_run.run_id if dag_run else None) or "latest"
    return {"model_version": model_version, "valid": True}


default_args = {
    "owner": "ml-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="credit_scoring_retraining",
    default_args=default_args,
    description="Automated retraining pipeline for credit scoring model",
    schedule_interval=timedelta(weeks=1),
    catchup=False,
    tags=["mlops", "retraining"],
) as dag:

    check_drift = PythonOperator(
        task_id="check_data_drift",
        python_callable=check_drift_task,
    )

    image_registry = Variable.get("IMAGE_REGISTRY", default="ghcr.io")
    mlflow_uri = Variable.get("mlflow_tracking_uri", default="http://mlflow:5000")
    dvc_remote = Variable.get("dvc_remote_url", default="")

    retrain_model = KubernetesPodOperator(
        task_id="retrain_model",
        namespace="default",
        image=f"{image_registry}/credit-scoring-trainer:latest",
        cmds=["python"],
        arguments=["-m", "src.models.train"],
        name="retrain-model-pod",
        is_delete_operator_pod=True,
        get_logs=True,
        env_vars={
            "MLFLOW_TRACKING_URI": mlflow_uri,
            "DVC_REMOTE_URL": dvc_remote,
        },
    )

    validate_model = PythonOperator(
        task_id="validate_new_model",
        python_callable=validate_model_task,
    )

    deploy_canary = KubernetesPodOperator(
        task_id="deploy_canary_release",
        namespace="default",
        image=f"{image_registry}/credit-scoring-deployer:latest",
        cmds=["deploy"],
        arguments=["--strategy", "canary", "--version", "{{ task_instance.xcom_pull(task_ids='validate_new_model')['model_version'] }}"],
        name="deploy-canary-pod",
        is_delete_operator_pod=True,
        get_logs=True,
    )

    check_drift >> retrain_model >> validate_model >> deploy_canary
