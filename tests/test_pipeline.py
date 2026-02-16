"""Тесты пайплайна модели"""

import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.models.pipeline import create_pipeline


@pytest.fixture
def sample_data():
    """Тестовые данные для пайплайна"""
    df = pd.DataFrame({
        "LIMIT_BAL": [20000.0, 50000.0, 90000.0],
        "AGE": [24, 37, 34],
        "BILL_AMT1": [3913.0, 46990.0, 29239.0],
        "PAY_AMT1": [0.0, 2000.0, 1518.0],
        "SEX": [1, 2, 2],
        "EDUCATION": [2, 2, 2],
        "MARRIAGE": [1, 2, 2],
        "PAY_0": [2, 0, 0],
        "PAY_2": [-1, 0, 0],
        "PAY_3": [-1, 0, 0],
        "PAY_4": [-1, 0, 0],
        "PAY_5": [-2, 0, 0],
        "PAY_6": [-2, 0, 0],
    })
    y = pd.Series([1, 0, 0])
    return df, y


def test_pipeline_fit_predict(sample_data):
    """Проверка, что пайплайн обучается и предсказывает корректно"""
    X, y = sample_data
    numeric = ["LIMIT_BAL", "AGE", "BILL_AMT1", "PAY_AMT1"]
    categorical = ["SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

    pipeline = create_pipeline(numeric, categorical)
    pipeline.fit(X, y)

    pred = pipeline.predict(X)
    assert len(pred) == len(y)
    assert set(pred) <= {0, 1}
