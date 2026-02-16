# Архитектура системы Credit Scoring MLOps

Краткое описание компонентов и потоков данных.

---

## Диаграмма архитектуры

```mermaid
flowchart TB
    subgraph Data["Данные"]
        RAW[raw/UCI_Credit_Card.csv]
        TRAIN[processed/train.csv]
        TEST[processed/test.csv]
        CURRENT[processed/current.csv]
    end

    subgraph Model["Модель"]
        TRAIN_PY[src/models/train.py]
        PKL[credit_default_model.pkl]
        ONNX[model.onnx]
        MLFLOW[(MLflow)]
    end

    subgraph API["API"]
        FASTAPI[FastAPI]
        PREDICT[/predict]
        METRICS[/metrics]
    end

    subgraph CICD["CI/CD"]
        GHA[GitHub Actions]
        BUILD[Build & Test]
        TRIVY[Trivy + Dockle]
        PUSH[Push Image]
        DEPLOY[Deploy K8s]
    end

    subgraph K8s["Kubernetes"]
        DEPLOYMENT[Deployment]
        SERVICE[Service]
        INGRESS[Ingress]
    end

    subgraph Monitoring["Мониторинг"]
        PROM[Prometheus]
        GRAFANA[Grafana]
        LOKI[Loki]
        ALERTS[Alerts]
    end

    subgraph Retraining["Переобучение"]
        AIRFLOW[Airflow]
        DRIFT_DAG[drift_check_trigger]
        RETRAIN_DAG[credit_scoring_retraining]
    end

    RAW --> TRAIN_PY
    TRAIN --> TRAIN_PY
    TEST --> TRAIN_PY
    TRAIN_PY --> PKL
    TRAIN_PY --> MLFLOW
    PKL --> ONNX

    PKL --> FASTAPI
    FASTAPI --> PREDICT
    FASTAPI --> METRICS

    GHA --> BUILD --> TRIVY --> PUSH --> DEPLOY
    DEPLOY --> DEPLOYMENT
    DEPLOYMENT --> SERVICE --> INGRESS

    METRICS --> PROM
    PROM --> GRAFANA
    LOKI --> GRAFANA
    PROM --> ALERTS

    CURRENT --> DRIFT_DAG
    DRIFT_DAG -->|drift_detected| RETRAIN_DAG
    RETRAIN_DAG --> TRAIN_PY
    RETRAIN_DAG --> DEPLOY
```

---

## Компоненты

### 1. Данные

| Компонент                         | Описание                                          |
| --------------------------------- | ------------------------------------------------- |
| **raw/**                          | Исходный датасет UCI Credit Card                  |
| **processed/train.csv, test.csv** | Разбивка 80/20, feature engineering               |
| **processed/current.csv**         | Текущие данные для дрифта (срез из API или теста) |
| **make_dataset.py**               | Подготовка данных, split                          |
| **validation.py**                 | Pandera-схема, Great Expectations в CI            |

### 2. Модель

| Компонент                    | Описание                                                    |
| ---------------------------- | ----------------------------------------------------------- |
| **pipeline.py**              | Sklearn Pipeline: preprocessor + GradientBoostingClassifier |
| **train.py**                 | Обучение, RandomizedSearchCV, MLflow, сохранение .pkl       |
| **credit_default_model.pkl** | Модель для API (joblib)                                     |
| **model.onnx**               | ONNX-версия (skl2onnx) для ускорения инференса              |
| **MLflow**                   | Эксперименты, метрики, артефакты                            |

### 3. API

| Компонент                             | Описание                                                           |
| ------------------------------------- | ------------------------------------------------------------------ |
| **FastAPI**                           | REST API, Swagger на /docs                                         |
| **/predict**                          | POST, JSON с признаками => default_prediction, default_probability |
| **/metrics**                          | Prometheus-метрики (requests, latency, process)                    |
| **prometheus-fastapi-instrumentator** | Автоматическая инструментация HTTP                                 |

### 4. CI/CD

| Компонент          | Описание                                                 |
| ------------------ | -------------------------------------------------------- |
| **GitHub Actions** | build => test => build-and-push-docker => deploy         |
| **Build**          | Black, Flake8, Trivy fs                                  |
| **Test**           | pytest, Pandera, Great Expectations                      |
| **Docker**         | Multi-stage: builder => dvc => final                     |
| **Trivy + Dockle** | Сканирование образа                                      |
| **Deploy**         | kubectl apply, staging (develop/v\*) / production (main) |

### 5. Kubernetes

| Компонент              | Описание                                  |
| ---------------------- | ----------------------------------------- |
| **Deployment**         | Rolling update, liveness/readiness probes |
| **Service**            | ClusterIP, порт 8000                      |
| **Ingress**            | Маршрутизация по host                     |
| **ConfigMap / Secret** | Конфигурация, секреты                     |

### 6. Мониторинг

| Компонент           | Описание                                 |
| ------------------- | ---------------------------------------- |
| **Prometheus**      | Сбор метрик API и K8s                    |
| **Grafana**         | Дашборды (API, инфраструктура)           |
| **Loki + Promtail** | Централизованные логи                    |
| **Alertmanager**    | Алерты (API down, high latency)          |
| **Runbook**         | docs/runbook.md — процедуры реагирования |

### 7. Переобучение (Airflow)

| Компонент                     | Описание                                                                |
| ----------------------------- | ----------------------------------------------------------------------- |
| **drift_check_trigger**       | Ежедневно: Evidently data drift => при drift TriggerDagRun              |
| **credit_scoring_retraining** | Еженедельно + по триггеру: check_drift => retrain => validate => deploy |
| **KubernetesPodOperator**     | retrain_model, deploy_canary_release в K8s                              |
| **Evidently**                 | Data drift, concept drift, drift_status.json                            |

---

## Потоки данных

1. **Обучение:** raw => make_dataset => train/test => train.py => .pkl + MLflow
2. **Инференс:** JSON => API => model.predict => JSON
3. **Дрифт:** current.csv => Evidently => drift_report.html, drift_status.json
4. **Переобучение:** drift_detected => Airflow => retrain => validate => deploy
5. **CI/CD:** push => Actions => build => test => image => kubectl apply
