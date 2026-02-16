# Airflow DAG — пайплайн переобучения

## retraining_dag.py

Цепочка задач:

1. **check_data_drift** — проверка data drift (Evidently)
2. **retrain_model** — переобучение в K8s (KubernetesPodOperator)
3. **validate_new_model** — валидация модели
4. **deploy_canary_release** — canary-деплой новой версии

## drift_trigger_dag.py

DAG проверки дрифта и условного запуска переобучения:

- **Расписание:** ежедневно (`@daily`)
- **check_data_drift** — запускает `evidently_drift_report.py --output-json`, читает `drift_detected`
- **trigger_retraining** — при дрифте запускает `credit_scoring_retraining` через `TriggerDagRunOperator`
- **skip_retraining** — при отсутствии дрифта — пропуск

## Триггеры переобучения (7.2)

| Триггер          | Описание                                                                           |
| ---------------- | ---------------------------------------------------------------------------------- |
| По расписанию    | Еженедельно (`retraining_dag`, `timedelta(weeks=1)`)                               |
| По данным/дрифту | Ежедневно `drift_check_trigger` => при `drift_detected` => `TriggerDagRunOperator` |

## Переменные Airflow

| Variable            | Описание                    | Пример             |
| ------------------- | --------------------------- | ------------------ |
| IMAGE_REGISTRY      | Registry для Docker-образов | ghcr.io/owner      |
| mlflow_tracking_uri | URI MLflow                  | http://mlflow:5000 |
| dvc_remote_url      | URL DVC remote              | s3://bucket/dvc    |

Admin => Variables => Add

## Размещение DAG

Скопировать в папку dags Airflow:

```bash
cp scripts/orchestration/retraining_dag.py $AIRFLOW_HOME/dags/
cp scripts/orchestration/drift_trigger_dag.py $AIRFLOW_HOME/dags/
# или симлинк
ln -s $(pwd)/scripts/orchestration/*.py $AIRFLOW_HOME/dags/
```

## Образы

- **credit-scoring-trainer** — образ с кодом обучения (python -m src.models.train)
- **credit-scoring-deployer** — образ для deploy (canary)

Создать Dockerfile для trainer и deployer в проекте.

## Расписание

- **credit_scoring_retraining:** еженедельно (`schedule_interval=timedelta(weeks=1)`) + по триггеру от drift_check_trigger
- **drift_check_trigger:** ежедневно (`@daily`)
