# Credit Default Prediction (PD-Model)

Сквозной автоматизированный пайплайн для PD-модели предсказания дефолта клиентов на датасете UCI Credit Card.

## Структура проекта

```
├── data/
│   ├── raw/           # Исходные данные (UCI_Credit_Card.csv)
│   ├── processed/     # train.csv, test.csv
│   └── expectations/  # Правила валидации
├── models/            # Обученные модели
├── notebooks/         # EDA и эксперименты
├── src/
│   ├── data/          # make_dataset.py, validation.py
│   ├── features/      # build_features.py
│   ├── models/        # pipeline.py, train.py, predict.py
│   └── api/           # FastAPI приложение
├── tests/             # Unit-тесты
├── scripts/           # Скрипты запуска и мониторинга
├── .github/workflows/ # CI/CD
├── dvc.yaml           # DVC pipeline
├── Dockerfile
└── requirements.txt
```

## Установка

```bash
pip install -r requirements.txt
```

## Запуск пайплайна

### 1. Подготовка данных

```bash
python src/data/make_dataset.py data/raw/UCI_Credit_Card.csv data/processed/
```

### 2. Обучение модели

```bash
python src/models/train.py
```

Один запуск: одна модель в `models/credit_default_model.pkl`, метрики в `metrics.json` и MLflow.

**5 экспериментов для MLflow:**

```bash
python src/models/train.py --experiments 5
```

В MLflow появятся 5 запусков с разными гиперпараметрами. Просмотр: `mlflow ui`.

### 3. EDA

Ноутбук разведки: `notebooks/01_eda.ipynb`.

### 4. DVC pipeline (опционально)

```bash
dvc init
dvc repro
```

### 5. Запуск API

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Документация: http://localhost:8000/docs

### 6. Docker

```bash
docker build -t credit-api .
docker run -p 8000:8000 credit-api
```

Или используйте скрипт: `./scripts/build_and_run.sh` (Linux/Mac) или `scripts\build_and_run.ps1` (Windows).

### 7. Пример запроса к API

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

### 8. Мониторинг дрифта

```bash
# Запустите API, затем:
python scripts/drift_monitor.py --api-url http://localhost:8000
```

## Демонстрация результатов

### Резюме проекта

Реализован сквозной пайплайн: загрузка и валидация данных (Pandera, Great Expectations в CI), feature engineering, обучение модели (Sklearn Pipeline + GradientBoosting), логирование в MLflow, DVC-пайплайн, REST API (FastAPI), Docker, мониторинг дрифта (PSI), unit-тесты и CI (GitHub Actions).

### Результаты модели (тестовая выборка)

После обучения (`python src/models/train.py` или `dvc repro`) метрики сохраняются в `metrics.json` и в MLflow. Пример итоговых метрик на отложенной выборке:

| Метрика   | Значение |
| --------- | -------- |
| ROC-AUC   | 0.776    |
| Precision | 0.67     |
| Recall    | 0.36     |
| F1-Score  | 0.47     |

При запуске `python src/models/train.py --experiments 5` в MLflow появляется 5 запусков с разными гиперпараметрами. лучший по AUC можно выбрать в UI (`mlflow ui` → http://localhost:5000).

### Выходы пайплайна

| Этап    | Вход                           | Выход                                                                 |
| ------- | ------------------------------ | --------------------------------------------------------------------- |
| prepare | `data/raw/UCI_Credit_Card.csv` | `data/processed/train.csv`, `test.csv`                                |
| train   | train.csv, test.csv            | `models/credit_default_model.pkl`, `metrics.json`, артефакты в MLflow |

### Пример ответа API

Запрос `POST /predict` с JSON признаков клиента возвращает класс и вероятность дефолта:

```json
{
  "default_prediction": 1,
  "default_probability": 0.82
}
```

Интерактивная документация и проверка: http://localhost:8000/docs после запуска `uvicorn src.api.app:app --reload`.

### Где посмотреть

- **Эксперименты и метрики:** `mlflow ui` → http://localhost:5000
- **CI (тесты, линтинг, валидация):** вкладка Actions в репозитории GitHub
- **EDA:** ноутбук `notebooks/01_eda.ipynb`

---

## Тестирование

```bash
pytest tests -v
```

![Image alt](https://github.com/mihgank-qwe/mpl_ops1/blob/main/images/img1.png)

```bash
black --check src tests
flake8 src tests --max-line-length=88
```

## MLflow

Просмотр экспериментов:

```bash
mlflow ui
```

Откройте http://localhost:5000
