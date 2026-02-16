# Мониторинг дрифта

## Evidently AI — Data Drift Report

Скрипт `scripts/evidently_drift_report.py` генерирует отчёт data drift.

### Запуск

```bash
# С current.csv (создать вручную или из API)
python scripts/evidently_drift_report.py

# Срез из test.csv (если current.csv отсутствует)
python scripts/evidently_drift_report.py --fallback-test

# Указать пути
python scripts/evidently_drift_report.py --reference data/processed/train.csv --current data/processed/current.csv --output monitoring/reports/drift_report.html

# С выводом drift_detected в JSON (для триггера Airflow)
python scripts/evidently_drift_report.py --fallback-test --output-json monitoring/reports/drift_status.json
```

### Входные данные

- **reference**: `data/processed/train.csv` — эталонные (тренировочные) данные
- **current**: `data/processed/current.csv` — текущие данные (или срез из API)

### Выход

- `monitoring/reports/drift_report.html` — HTML-отчёт с DataDriftTable
- `monitoring/reports/drift_status.json` — при `--output-json` флаг `drift_detected` для триггера переобучения

## Concept Drift & Model Quality

Скрипт `scripts/evidently_concept_drift_report.py` — мониторинг concept drift и деградации качества:

- **Target Drift** — дрифт целевой переменной
- **Prediction Drift** — дрифт предсказаний
- **Classification Quality** — accuracy, precision, recall, ROC AUC

```bash
python scripts/evidently_concept_drift_report.py --fallback-test
```

Выход: `monitoring/reports/concept_drift_report.html`

### Получение current из API

Для получения current среза из API можно использовать:

```python
# Пример: скрипт сбора данных из API
import requests
import pandas as pd

# Запросы к /predict, сохранение в current.csv
```
