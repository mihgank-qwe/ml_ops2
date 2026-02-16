"""Утилиты для предсказаний"""

from pathlib import Path

import joblib
import pandas as pd


def load_model(model_path: str | Path = None):
    """Метод загружает обученную модель с диска"""
    if model_path is None:
        project_root = Path(__file__).resolve().parents[2]
        model_path = project_root / "models" / "credit_default_model.pkl"

    return joblib.load(model_path)


def predict(model, data: pd.DataFrame):
    """Метод делает предсказания и возвращает (класс, вероятность)"""
    predictions = model.predict(data)
    probabilities = model.predict_proba(data)[:, 1]
    return predictions, probabilities
