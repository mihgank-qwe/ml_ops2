"""Создание признаков для предсказания дефолта"""

import pandas as pd
import numpy as np

# Колонки для агрегации
PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLS = [
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
]
PAY_AMT_COLS = ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]


def add_aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Метод добавляет агрегированные признаки из истории платежей"""
    df = df.copy()

    if all(c in df.columns for c in PAY_COLS):
        df["PAY_MEAN"] = df[PAY_COLS].mean(axis=1)
        df["PAY_MAX"] = df[PAY_COLS].max(axis=1)
        df["PAY_MIN"] = df[PAY_COLS].min(axis=1)

    if all(c in df.columns for c in BILL_COLS):
        df["BILL_AMT_MEAN"] = df[BILL_COLS].mean(axis=1)
        df["BILL_AMT_MAX"] = df[BILL_COLS].max(axis=1)

    if all(c in df.columns for c in PAY_AMT_COLS):
        df["PAY_AMT_MEAN"] = df[PAY_AMT_COLS].mean(axis=1)
        df["PAY_AMT_SUM"] = df[PAY_AMT_COLS].sum(axis=1)

    # Отношение платежей к сумме счёта
    if "BILL_AMT_MEAN" in df.columns and "PAY_AMT_MEAN" in df.columns:
        df["PAY_TO_BILL_RATIO"] = np.where(
            df["BILL_AMT_MEAN"] > 0,
            df["PAY_AMT_MEAN"] / df["BILL_AMT_MEAN"],
            0,
        )

    return df


def add_age_bins(df: pd.DataFrame, age_col: str = "AGE") -> pd.DataFrame:
    """Метод добавляет биннинг возраста (18-25, 26-35, 36-50, 50+)"""
    df = df.copy()
    if age_col not in df.columns:
        return df

    bins = [0, 25, 35, 50, 120]
    labels = ["18-25", "26-35", "36-50", "50+"]
    df["AGE_BIN"] = pd.cut(
        df[age_col].clip(lower=18, upper=100),
        bins=bins,
        labels=labels,
        include_lowest=True,
    )
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Метод применяет все шаги создания признаков"""
    df = add_aggregate_features(df)
    df = add_age_bins(df)
    return df
