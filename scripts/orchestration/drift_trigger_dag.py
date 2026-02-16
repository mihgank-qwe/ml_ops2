"""
Airflow DAG: проверка data drift и триггер переобучения при обнаружении дрифта.

Триггер по данным/дрифту: при drift_detected=True запускает credit_scoring_retraining.

Расписание: ежедневно (schedule_interval=@daily).
При обнаружении дрифта — TriggerDagRunOperator запускает DAG переобучения.

Размещение: скопировать или симлинк в AIRFLOW_HOME/dags/
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator


def check_drift_and_decide(**context):
    """
    Запускает evidently_drift_report с --output-json, читает drift_detected.
    Возвращает task_id для ветвления: trigger_retraining или skip_retraining.
    """
    import json
    import subprocess
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    json_path = project_root / "monitoring" / "reports" / "drift_status.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "evidently_drift_report.py"),
            "--fallback-test",
            "--output-json",
            str(json_path),
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"drift report failed: {result.stderr}")

    drift_detected = True
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
            drift_detected = data.get("drift_detected", True)

    return "trigger_retraining" if drift_detected else "skip_retraining"


default_args = {
    "owner": "ml-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="drift_check_trigger",
    default_args=default_args,
    description="Check data drift and trigger retraining when drift detected",
    schedule_interval="@daily",
    catchup=False,
    tags=["mlops", "drift", "trigger"],
) as dag:

    check_drift = BranchPythonOperator(
        task_id="check_data_drift",
        python_callable=check_drift_and_decide,
    )

    trigger_retraining = TriggerDagRunOperator(
        task_id="trigger_retraining",
        trigger_dag_id="credit_scoring_retraining",
        wait_for_completion=False,
    )

    skip_retraining = EmptyOperator(task_id="skip_retraining")

    check_drift >> [trigger_retraining, skip_retraining]
