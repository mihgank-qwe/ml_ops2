"""Тесты валидации данных"""

import pytest
import pandas as pd

from src.data.validation import validate_credit_data


def test_validation_passes_on_valid_data():
    """Проверка, что валидация проходит на корректных данных"""
    valid_df = pd.DataFrame({
        "LIMIT_BAL": [20000.0, 50000.0],
        "SEX": [1, 2],
        "EDUCATION": [2, 2],
        "MARRIAGE": [1, 2],
        "AGE": [24, 37],
        "PAY_0": [2, 0],
        "BILL_AMT1": [3913.0, 46990.0],
        "PAY_AMT1": [0.0, 2000.0],
        "default.payment.next.month": [1, 0],
    })
    result = validate_credit_data(valid_df)
    assert len(result) == 2


def test_validation_fails_on_null_target():
    """Проверка, что валидация падает при null в целевой переменной"""
    invalid_df = pd.DataFrame({
        "LIMIT_BAL": [20000.0],
        "SEX": [1],
        "EDUCATION": [2],
        "MARRIAGE": [1],
        "AGE": [24],
        "PAY_0": [2],
        "BILL_AMT1": [3913.0],
        "PAY_AMT1": [0.0],
        "default.payment.next.month": [None],
    })
    with pytest.raises(Exception):
        validate_credit_data(invalid_df)


def test_validation_fails_on_invalid_target_values():
    """Проверка, что валидация падает при значениях целевой не 0 и не 1"""
    invalid_df = pd.DataFrame({
        "LIMIT_BAL": [20000.0],
        "SEX": [1],
        "EDUCATION": [2],
        "MARRIAGE": [1],
        "AGE": [24],
        "PAY_0": [2],
        "BILL_AMT1": [3913.0],
        "PAY_AMT1": [0.0],
        "default.payment.next.month": [2],
    })
    with pytest.raises(Exception):
        validate_credit_data(invalid_df)


def test_validation_fails_on_invalid_age():
    """Проверка, что валидация падает при возрасте вне 18-100"""
    invalid_df = pd.DataFrame({
        "LIMIT_BAL": [20000.0],
        "SEX": [1],
        "EDUCATION": [2],
        "MARRIAGE": [1],
        "AGE": [17],
        "PAY_0": [2],
        "BILL_AMT1": [3913.0],
        "PAY_AMT1": [0.0],
        "default.payment.next.month": [0],
    })
    with pytest.raises(Exception):
        validate_credit_data(invalid_df)


def test_validate_processed_data_file():
    """Проверка, что валидация проходит на обработанных данных"""
    from pathlib import Path
    from src.data.validation import validate_data_file

    train_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "train.csv"
    if train_path.exists():
        assert validate_data_file(train_path) is True
