"""
Скрипт мониторинга data drift (Evidently AI).

Загружает reference (train.csv) и current данные, генерирует отчёт DataDriftPreset,
сохраняет HTML в monitoring/reports/drift_report.html.

Использование:
  python scripts/evidently_drift_report.py
  python scripts/evidently_drift_report.py --current data/processed/current.csv
  python scripts/evidently_drift_report.py --current data/processed/test.csv  # срез из теста
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Корень проекта
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(description="Data drift report (Evidently AI)")
    parser.add_argument(
        "--reference",
        default=project_root / "data" / "processed" / "train.csv",
        type=Path,
        help="Reference data (training)",
    )
    parser.add_argument(
        "--current",
        default=project_root / "data" / "processed" / "current.csv",
        type=Path,
        help="Current data (или срез из test.csv / API)",
    )
    parser.add_argument(
        "--output",
        default=project_root / "monitoring" / "reports" / "drift_report.html",
        type=Path,
        help="Output HTML path",
    )
    parser.add_argument(
        "--fallback-test",
        action="store_true",
        help="Если current.csv отсутствует — использовать срез из test.csv",
    )
    args = parser.parse_args()

    reference_path = args.reference
    current_path = args.current
    output_path = args.output

    if not reference_path.exists():
        print(f"Reference не найден: {reference_path}")
        print("Запустите: python src/data/make_dataset.py data/raw/UCI_Credit_Card.csv data/processed/")
        sys.exit(1)

    # Загружаем эталонные данные (тренировочные)
    reference_data = pd.read_csv(reference_path)
    print(f"Reference: {reference_path} ({len(reference_data)} rows)")

    # Загружаем текущие данные
    if not current_path.exists():
        if args.fallback_test:
            test_path = project_root / "data" / "processed" / "test.csv"
            if test_path.exists():
                test_df = pd.read_csv(test_path)
                current_data = test_df.sample(n=min(1000, len(test_df)), random_state=42)
                print(f"Current: срез из {test_path} ({len(current_data)} rows)")
            else:
                print(f"Current не найден: {current_path}, test.csv тоже отсутствует")
                sys.exit(1)
        else:
            print(f"Current не найден: {current_path}")
            print("Создайте current.csv или используйте --fallback-test для среза из test.csv")
            sys.exit(1)
    else:
        current_data = pd.read_csv(current_path)
        print(f"Current: {current_path} ({len(current_data)} rows)")

    # Проверяем совпадение колонок
    ref_cols = set(reference_data.columns)
    cur_cols = set(current_data.columns)
    common = ref_cols & cur_cols
    if len(common) < len(ref_cols):
        missing = ref_cols - cur_cols
        print(f"Предупреждение: в current отсутствуют колонки {missing}")

    # Evidently: DataDriftTable (по аналогии с zadanie/img5) или DataDriftPreset
    try:
        from evidently.report import Report
        from evidently.metrics import DataDriftTable
        report = Report(metrics=[DataDriftTable()])
    except ImportError:
        try:
            from evidently.report import Report
            from evidently.presets import DataDriftPreset
            report = Report(metrics=[DataDriftPreset()])
        except ImportError:
            from evidently.report import Report
            from evidently.metric_preset import DataDriftPreset
            report = Report(metrics=[DataDriftPreset()])
    result = report.run(reference_data=reference_data, current_data=current_data)

    # Сохраняем HTML (result или report в зависимости от версии Evidently)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    obj = result if result is not None else report
    obj.save_html(str(output_path))
    print(f"Отчёт сохранён: {output_path}")


if __name__ == "__main__":
    main()
