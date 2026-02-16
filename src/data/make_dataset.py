"""Загрузка, очистка и подготовка датасета для предсказания дефолта"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# Добавляем корень проекта в путь для импортов
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.features.build_features import build_features


def load_and_clean(raw_path: str) -> pd.DataFrame:
    """Метод загружает CSV и очищает данные"""
    df = pd.read_csv(raw_path)

    # Убираем ID
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])

    df = df.drop_duplicates()

    # Оставляем возраст 18-100
    if "AGE" in df.columns:
        df = df[(df["AGE"] >= 18) & (df["AGE"] <= 100)]

    return df


def main():
    parser = argparse.ArgumentParser(description="Подготовка датасета")
    parser.add_argument("input_path", type=str, help="Путь к UCI_Credit_Card")
    parser.add_argument("output_dir", type=str, help="Папка для train и test")
    parser.add_argument("--test-size", type=float, default=0.2, help="Доля теста")
    parser.add_argument("--random-state", type=int, default=42, help="Сид для воспроизводимости")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Загрузка и очистка данных")
    df = load_and_clean(str(input_path))

    print("Создание признаков")
    df = build_features(df)

    target_col = "default.payment.next.month"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Убираем AGE_BIN - категориальный признак => не используем в пайплайне
    if "AGE_BIN" in X.columns:
        X = X.drop(columns=["AGE_BIN"])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    train_df = X_train.copy()
    train_df[target_col] = y_train
    test_df = X_test.copy()
    test_df[target_col] = y_test

    train_path = output_dir / "train.csv"
    test_path = output_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"Сохранено в train: {train_path} ({len(train_df)} строк)")
    print(f"Сохранено в test: {test_path} ({len(test_df)} строк)")


if __name__ == "__main__":
    main()
