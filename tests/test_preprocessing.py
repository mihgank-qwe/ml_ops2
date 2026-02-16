"""Тесты создания признаков"""

import pandas as pd
import pytest

from src.features.build_features import (
    add_aggregate_features,
    add_age_bins,
    build_features,
)


@pytest.fixture
def sample_df():
    """Метод возвращает тестовые данные по кредитам"""
    return pd.DataFrame({
        "LIMIT_BAL": [20000, 50000],
        "SEX": [1, 2],
        "EDUCATION": [2, 2],
        "MARRIAGE": [1, 2],
        "AGE": [24, 37],
        "PAY_0": [2, 0],
        "PAY_2": [-1, 0],
        "PAY_3": [-1, 0],
        "PAY_4": [-1, 0],
        "PAY_5": [-2, 0],
        "PAY_6": [-2, 0],
        "BILL_AMT1": [3913.0, 46990.0],
        "BILL_AMT2": [3102.0, 48233.0],
        "BILL_AMT3": [689.0, 49291.0],
        "BILL_AMT4": [0.0, 28314.0],
        "BILL_AMT5": [0.0, 28959.0],
        "BILL_AMT6": [0.0, 29547.0],
        "PAY_AMT1": [0.0, 2000.0],
        "PAY_AMT2": [689.0, 2019.0],
        "PAY_AMT3": [0.0, 1200.0],
        "PAY_AMT4": [0.0, 1100.0],
        "PAY_AMT5": [0.0, 1069.0],
        "PAY_AMT6": [0.0, 1000.0],
    })


def test_add_aggregate_features(sample_df): 
    """Проверка, что агрегаты добавляются корректно"""
    result = add_aggregate_features(sample_df)
    assert "PAY_MEAN" in result.columns
    assert "PAY_MAX" in result.columns
    assert "PAY_MIN" in result.columns
    assert "BILL_AMT_MEAN" in result.columns
    assert "PAY_AMT_MEAN" in result.columns
    assert "PAY_TO_BILL_RATIO" in result.columns


def test_add_age_bins(sample_df):
    """Проверка, что биннинг возраста создаётся корректно"""
    result = add_age_bins(sample_df)
    assert "AGE_BIN" in result.columns
    assert result["AGE_BIN"].dtype.name == "category"


def test_build_features(sample_df):
    """Проверка, что полное создание признаков работает корректно"""
    result = build_features(sample_df)
    assert len(result) == 2
    assert "PAY_MEAN" in result.columns
    assert "AGE_BIN" in result.columns
