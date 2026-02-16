"""
Скрипт мониторинга дрифта

Берёт выборку из теста как новые данные, отправляет в API,
считает PSI (индекс стабильности) для признаков и вероятностей
"""

import argparse
import requests
from pathlib import Path
import sys

import numpy as np
import pandas as pd

# Корень проекта
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Считает PSI между двумя распределениями"""
    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1)[1:-1])
    breakpoints = np.unique(breakpoints)
    if len(breakpoints) < 2:
        breakpoints = np.percentile(
            np.concatenate([expected, actual]), np.linspace(0, 100, bins + 1)[1:-1]
        )

    expected_percents = np.histogram(
        expected, bins=np.concatenate([[-np.inf], breakpoints, [np.inf]])
    )[0] / len(expected)
    actual_percents = np.histogram(
        actual, bins=np.concatenate([[-np.inf], breakpoints, [np.inf]])
    )[0] / len(actual)

    expected_percents = np.clip(expected_percents, 0.001, 1)
    actual_percents = np.clip(actual_percents, 0.001, 1)

    psi = np.sum(
        (actual_percents - expected_percents)
        * np.log(actual_percents / expected_percents)
    )
    return float(psi)


def main():
    parser = argparse.ArgumentParser(description="Мониторинг дрифта данных")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL API")
    parser.add_argument("--sample-size", type=int, default=100, help="Число записей для проверки")
    args = parser.parse_args()

    train_path = project_root / "data" / "processed" / "train.csv"
    test_path = project_root / "data" / "processed" / "test.csv"

    if not train_path.exists() or not test_path.exists():
        print("Сначала надо запустить make_dataset для создания train.csv и test.csv")
        sys.exit(1)

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Выборка из теста как новые данные
    sample = test_df.sample(n=min(args.sample_size, len(test_df)), random_state=42)

    target_col = "default.payment.next.month"
    feature_cols = [c for c in sample.columns if c != target_col]

    # Получаем предсказания от API
    api_url = args.api_url.rstrip("/")
    try:
        response = requests.get(f"{api_url}/")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"API недоступен по {api_url}: {e}")
        print("Сначала запустите API: uvicorn src.api.app:app --reload")
        sys.exit(1)

    probabilities = []
    for _, row in sample.iterrows():
        payload = row[feature_cols].to_dict()
        try:
            resp = requests.post(f"{api_url}/predict", json=payload, timeout=5)
            resp.raise_for_status()
            probabilities.append(resp.json()["default_probability"])
        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            sys.exit(1)

    probabilities = np.array(probabilities)

    # Считаем PSI для ключевых признаков
    key_features = ["LIMIT_BAL", "AGE", "PAY_0", "BILL_AMT1", "PAY_AMT1"]
    key_features = [f for f in key_features if f in train_df.columns]

    print("Индекс стабильности (PSI):")
    print("-" * 40)

    for feat in key_features:
        psi = calculate_psi(train_df[feat].values, sample[feat].values)
        status = "OK" if psi < 0.1 else "Умеренно" if psi < 0.25 else "Высокий"
        print(f"  {feat}: {psi:.4f} ({status})")

    # PSI для вероятностей (приближение по целевой переменной)
    train_proba_approx = train_df[target_col].values.astype(float)
    psi_proba = calculate_psi(train_proba_approx, probabilities)
    status = "OK" if psi_proba < 0.1 else "Умеренно" if psi_proba < 0.25 else "Высокий"
    print(f"  predicted_probability: {psi_proba:.4f} ({status})")


if __name__ == "__main__":
    main()
