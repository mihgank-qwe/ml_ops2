# Credit Default Prediction (PD-Model)

Сквозной MLOps-пайплайн для PD-модели предсказания дефолта клиентов на датасете UCI Credit Card.

---

## Структура репозитория

```
├── data/
│   ├── raw/              # Исходные данные (UCI_Credit_Card.csv)
│   ├── processed/        # train.csv, test.csv, current.csv
│   └── expectations/     # Great Expectations
├── models/               # Обученные модели (.pkl, .onnx)
├── notebooks/            # EDA и эксперименты
├── src/
│   ├── data/             # make_dataset.py, validation.py
│   ├── features/         # build_features.py
│   ├── models/           # pipeline.py, train.py
│   └── api/              # FastAPI приложение
├── tests/                # Unit-тесты
├── scripts/
│   ├── model_training/   # onnx_conversion, benchmark, load_test
│   ├── orchestration/    # Airflow DAG (retraining, drift_trigger)
│   └── evidently_*.py   # Дрифт-отчёты
├── monitoring/
│   └── reports/         # drift_report.html, drift_status.json
├── deployment/
│   ├── kubernetes/       # Deployment, Service, Ingress, ConfigMap
│   └── monitoring/      # Prometheus, Grafana, Loki, Promtail
├── infrastructure/       # Terraform (Yandex Cloud)
├── docs/                 # Runbook, архитектура
├── .github/workflows/    # CI/CD
├── dvc.yaml              # DVC pipeline
├── Dockerfile
└── requirements.txt
```

---

## Быстрый старт

### 1. Установка

```bash
pip install -r requirements.txt
```

### 2. Подготовка данных

```bash
python src/data/make_dataset.py data/raw/UCI_Credit_Card.csv data/processed/
```

### 3. Обучение модели

```bash
python -m src.models.train
```

Модель сохраняется в `models/credit_default_model.pkl`, метрики — в `metrics.json` и MLflow.

**5 экспериментов (гиперпараметры):**

```bash
python -m src.models.train --experiments 5
```

### 4. Запуск API

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: http://localhost:8000/docs
- Метрики: http://localhost:8000/metrics

---

## Обучение

| Команда                                      | Описание                                                |
| -------------------------------------------- | ------------------------------------------------------- |
| `python -m src.models.train`                 | Один запуск, модель в `models/credit_default_model.pkl` |
| `python -m src.models.train --experiments 5` | 5 экспериментов в MLflow                                |
| `dvc repro`                                  | Полный DVC-пайплайн (данные => обучение)                |

**Выходы:** `models/credit_default_model.pkl`, `metrics.json`, артефакты в MLflow (`mlflow ui`).

---

## ONNX

Конвертация sklearn-модели в ONNX для ускорения инференса:

```bash
# 1. Обучить NN-модель (если нужна ONNX-версия)
python scripts/model_training/train_nn.py

# 2. Конвертация в ONNX
python scripts/model_training/onnx_conversion.py

# 3. Валидация (сравнение sklearn vs ONNX)
python scripts/model_training/validate_onnx.py

# 4. Бенчмарк производительности
python scripts/model_training/benchmark_inference.py
```

**Выходы:** `models/model.onnx`, `models/model_quantized.onnx`, `models/benchmark_results.json`.

Подробнее: [docs/BENCHMARK_REPORT.md](docs/BENCHMARK_REPORT.md).

---

## API

**FastAPI** с эндпоинтами:

| Endpoint   | Метод | Описание                                 |
| ---------- | ----- | ---------------------------------------- |
| `/predict` | POST  | Предсказание дефолта (JSON с признаками) |
| `/metrics` | GET   | Prometheus-метрики                       |
| `/docs`    | GET   | Swagger UI                               |

**Пример запроса:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "LIMIT_BAL": 20000, "SEX": 1, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 24,
    "PAY_0": 2, "PAY_2": -1, "PAY_3": -1, "PAY_4": -1, "PAY_5": -2, "PAY_6": -2,
    "BILL_AMT1": 3913, "BILL_AMT2": 3102, "BILL_AMT3": 689, "BILL_AMT4": 0,
    "BILL_AMT5": 0, "BILL_AMT6": 0,
    "PAY_AMT1": 0, "PAY_AMT2": 689, "PAY_AMT3": 0, "PAY_AMT4": 0, "PAY_AMT5": 0, "PAY_AMT6": 0,
    "PAY_MEAN": -1.0, "PAY_MAX": 2, "PAY_MIN": -2,
    "BILL_AMT_MEAN": 1301.0, "BILL_AMT_MAX": 3913,
    "PAY_AMT_MEAN": 114.83, "PAY_AMT_SUM": 689, "PAY_TO_BILL_RATIO": 0.088
  }'
```

---

## Docker

```bash
docker build -t credit-scoring-api .
docker run -p 8000:8000 credit-scoring-api
```

Или: `./scripts/build_and_run.sh` (Linux/Mac) / `scripts\build_and_run.ps1` (Windows).

---

## Kubernetes

```bash
kubectl apply -f deployment/kubernetes/
```

Манифесты: Deployment, Service, Ingress, ConfigMap, Secret. Подробнее: [deployment/kubernetes/README.md](deployment/kubernetes/README.md).

---

## Мониторинг

**Prometheus + Grafana + Loki + Promtail** — см. [deployment/monitoring/README.md](deployment/monitoring/README.md).

- **Метрики API:** `/metrics` (requests, latency, CPU, memory)
- **Дашборды:** API, инфраструктура K8s
- **Логи:** Loki + Promtail
- **Алерты:** Prometheus rules, [docs/runbook.md](docs/runbook.md)

---

## Дрифт

**Evidently AI** — data drift и concept drift:

```bash
# Data drift
python scripts/evidently_drift_report.py --fallback-test

# Concept drift + качество модели
python scripts/evidently_concept_drift_report.py --fallback-test

# JSON для триггера Airflow
python scripts/evidently_drift_report.py --fallback-test --output-json monitoring/reports/drift_status.json
```

Отчёты: `monitoring/reports/drift_report.html`, `concept_drift_report.html`. Подробнее: [monitoring/README.md](monitoring/README.md).

---

## Airflow (переобучение)

DAG-и в `scripts/orchestration/`:

| DAG                         | Расписание                | Описание                                       |
| --------------------------- | ------------------------- | ---------------------------------------------- |
| `credit_scoring_retraining` | Еженедельно + по триггеру | check_drift => retrain => validate => deploy   |
| `drift_check_trigger`       | Ежедневно                 | Проверка дрифта => при drift запуск retraining |

**Размещение:**

```bash
cp scripts/orchestration/*.py $AIRFLOW_HOME/dags/
```

Подробнее: [scripts/orchestration/README.md](scripts/orchestration/README.md).

---

## CI/CD

GitHub Actions: build => test => Trivy/Dockle => build-and-push-docker => deploy.

| Окружение  | Триггер              | Namespace  |
| ---------- | -------------------- | ---------- |
| Staging    | `develop`, теги `v*` | staging    |
| Production | `main`               | production |

Подробнее: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml).

---

## Тестирование

```bash
pytest tests -v
black --check src tests
flake8 src tests --max-line-length=88
```

---

## Документация

| Документ                                             | Описание                 |
| ---------------------------------------------------- | ------------------------ |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)         | Архитектура системы      |
| [docs/runbook.md](docs/runbook.md)                   | Реагирование на алерты   |
| [docs/BENCHMARK_REPORT.md](docs/BENCHMARK_REPORT.md) | Бенчмарк ONNX            |
| [infrastructure/README.md](infrastructure/README.md) | Terraform (Yandex Cloud) |
