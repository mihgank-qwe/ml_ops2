"""
Мониторинг concept drift и деградации качества модели (Evidently AI).

Метрики по целевой переменной (target) и предсказаниям (prediction):
- Target Drift — дрифт распределения целевой переменной
- Prediction Drift — дрифт предсказаний
- Classification Quality — accuracy, precision, recall, ROC AUC (деградация качества)

Использование:
  python scripts/evidently_concept_drift_report.py --fallback-test
  python scripts/evidently_concept_drift_report.py --current data/processed/current.csv
"""

import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd

# Корень проекта
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

TARGET_COL = "default.payment.next.month"
PREDICTION_COL = "prediction"
PREDICTION_PROBA_COL = "prediction_proba"


def get_predictions(model, df: pd.DataFrame, feature_cols: list) -> tuple:
    """Получить предсказания модели (класс и вероятность)."""
    X = df[feature_cols]
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]  # вероятность класса 1
    return pred, proba


def main():
    parser = argparse.ArgumentParser(description="Concept drift & model quality report (Evidently AI)")
    parser.add_argument(
        "--reference",
        default=project_root / "data" / "processed" / "train.csv",
        type=Path,
        help="Reference data",
    )
    parser.add_argument(
        "--current",
        default=project_root / "data" / "processed" / "current.csv",
        type=Path,
        help="Current data",
    )
    parser.add_argument(
        "--output",
        default=project_root / "monitoring" / "reports" / "concept_drift_report.html",
        type=Path,
        help="Output HTML path",
    )
    parser.add_argument(
        "--fallback-test",
        action="store_true",
        help="Если current отсутствует — срез из test.csv",
    )
    parser.add_argument(
        "--model",
        default=project_root / "models" / "credit_default_model.pkl",
        type=Path,
        help="Path to model",
    )
    args = parser.parse_args()

    # Загрузка модели
    if not args.model.exists():
        print(f"Модель не найдена: {args.model}")
        print("Обучите модель и сохраните в models/credit_default_model.pkl")
        sys.exit(1)
    model = joblib.load(args.model)

    # Загрузка reference
    if not args.reference.exists():
        print(f"Reference не найден: {args.reference}")
        sys.exit(1)
    reference_data = pd.read_csv(args.reference)
    print(f"Reference: {args.reference} ({len(reference_data)} rows)")

    # Загрузка current
    if not args.current.exists():
        if args.fallback_test:
            test_path = project_root / "data" / "processed" / "test.csv"
            if test_path.exists():
                test_df = pd.read_csv(test_path)
                current_data = test_df.sample(n=min(1000, len(test_df)), random_state=42)
                print(f"Current: срез из {test_path} ({len(current_data)} rows)")
            else:
                print("Current и test.csv не найдены")
                sys.exit(1)
        else:
            print(f"Current не найден: {args.current}. Используйте --fallback-test")
            sys.exit(1)
    else:
        current_data = pd.read_csv(args.current)
        print(f"Current: {args.current} ({len(current_data)} rows)")

    # Признаки (без target)
    feature_cols = [c for c in reference_data.columns if c != TARGET_COL]
    if TARGET_COL not in reference_data.columns or TARGET_COL not in current_data.columns:
        print(f"Колонка {TARGET_COL} отсутствует в данных")
        sys.exit(1)

    # Предсказания
    reference_data = reference_data.copy()
    current_data = current_data.copy()
    ref_pred, ref_proba = get_predictions(model, reference_data, feature_cols)
    cur_pred, cur_proba = get_predictions(model, current_data, feature_cols)
    reference_data[PREDICTION_COL] = ref_pred
    reference_data[PREDICTION_PROBA_COL] = ref_proba
    current_data[PREDICTION_COL] = cur_pred
    current_data[PREDICTION_PROBA_COL] = cur_proba

    # Evidently: Data Drift (включает target/prediction drift) + Classification Quality
    from evidently.report import Report

    metrics = []
    try:
        from evidently.presets import DataDriftPreset
        metrics.append(DataDriftPreset())
    except ImportError:
        from evidently.metric_preset import DataDriftPreset
        metrics.append(DataDriftPreset())

    try:
        from evidently.presets import ClassificationPreset
        metrics.append(ClassificationPreset())
    except ImportError:
        try:
            from evidently.metric_preset import ClassificationPreset
            metrics.append(ClassificationPreset())
        except ImportError:
            pass

    try:
        from evidently.presets import TargetDriftPreset
        metrics.append(TargetDriftPreset())
    except ImportError:
        try:
            from evidently.metric_preset import TargetDriftPreset
            metrics.append(TargetDriftPreset())
        except ImportError:
            pass

    report = Report(metrics=metrics)

    # Column mapping
    column_mapping = None
    try:
        from evidently import ColumnMapping
        column_mapping = ColumnMapping(
            target=TARGET_COL,
            prediction=PREDICTION_COL,
            prediction_probas=PREDICTION_PROBA_COL,
        )
    except ImportError:
        pass

    # run(current, ref) — first current, second reference
    if column_mapping is not None:
        result = report.run(current_data, reference_data, column_mapping=column_mapping)
    else:
        result = report.run(current_data, reference_data)

    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    obj = result if result is not None else report
    obj.save_html(str(output_path))
    print(f"Отчёт сохранён: {output_path}")


if __name__ == "__main__":
    main()
