"""Валидация данных с помощью Pandera"""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa


def get_credit_data_schema() -> pa.DataFrameSchema:
    """Схема проверки: колонки, null, возраст 18-100, целевая 0 или 1"""
    return pa.DataFrameSchema(
        {
            "LIMIT_BAL": pa.Column(
                pa.Float, pa.Check.greater_than_or_equal_to(0), nullable=False
            ),
            "SEX": pa.Column(pa.Int, pa.Check.isin([1, 2]), nullable=False),
            "EDUCATION": pa.Column(
                pa.Int, pa.Check.greater_than_or_equal_to(0), nullable=False
            ),
            "MARRIAGE": pa.Column(
                pa.Int, pa.Check.greater_than_or_equal_to(0), nullable=False
            ),
            "AGE": pa.Column(pa.Int, pa.Check.in_range(18, 100), nullable=False),
            "PAY_0": pa.Column(pa.Int, nullable=False),
            "BILL_AMT1": pa.Column(pa.Float, nullable=False),
            "PAY_AMT1": pa.Column(
                pa.Float, pa.Check.greater_than_or_equal_to(0), nullable=False
            ),
            "default.payment.next.month": pa.Column(
                pa.Int, pa.Check.isin([0, 1]), nullable=False
            ),
        },
        strict=False,  # Разрешаем доп. колонки
    )


def validate_credit_data(df: pd.DataFrame) -> pd.DataFrame:
    """Метод проверяет данные по схеме"""
    schema = get_credit_data_schema()
    return schema.validate(df)


def validate_data_file(file_path: str | Path) -> bool:
    """Метод проверяет CSV-файл по схеме"""
    df = pd.read_csv(file_path)
    validate_credit_data(df)
    return True
