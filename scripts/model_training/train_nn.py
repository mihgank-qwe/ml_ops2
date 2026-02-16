"""
Обучение нейронной сети (MLPClassifier) для кредитного скоринга
Сохраняет модель в models/credit_nn.pkl
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import pandas as pd
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.models.pipeline import create_nn_pipeline
from src.models.train import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET_COL,
    load_data,
)


def main():
    X_train, X_test, y_train, y_test = load_data()

    pipeline = create_nn_pipeline(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    model_path = project_root / "models" / "credit_nn.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    metrics = {
        "auc": auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
    metrics_path = project_root / "models" / "credit_nn_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(
        f"NN metrics: AUC={auc:.4f}, Precision={precision:.4f}, "
        f"Recall={recall:.4f}, F1={f1:.4f}"
    )
    print(f"Модель сохранена: {model_path}")
    print(f"Метрики сохранены: {metrics_path}")


if __name__ == "__main__":
    main()
