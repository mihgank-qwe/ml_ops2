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
```

### Входные данные

- **reference**: `data/processed/train.csv` — эталонные (тренировочные) данные
- **current**: `data/processed/current.csv` — текущие данные (или срез из API)

### Выход

- `monitoring/reports/drift_report.html` — HTML-отчёт с DataDriftTable

### Получение current из API

Для получения current среза из API можно использовать:

```python
# Пример: скрипт сбора данных из API
import requests
import pandas as pd

# Запросы к /predict, сохранение в current.csv
```
