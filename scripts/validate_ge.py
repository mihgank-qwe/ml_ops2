"""
Валидация данных с помощью Great Expectations для CI

Проверяет ключевые колонки, null, возраст 18-100, целевая 0/1
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd


def main():
    train_path = project_root / "data" / "processed" / "train.csv"
    if not train_path.exists():
        print("Файл train.csv не найден. Сначала надо запустить make_dataset")
        sys.exit(1)

    df = pd.read_csv(train_path)

    try:
        import great_expectations as gx
    except ImportError:
        print("Установите great_expectations: pip install great_expectations")
        sys.exit(1)

    ge_df = gx.from_pandas(df)
    ge_df.expect_column_to_exist("LIMIT_BAL")
    ge_df.expect_column_values_to_not_be_null("LIMIT_BAL")
    ge_df.expect_column_to_exist("AGE")
    ge_df.expect_column_values_to_be_between("AGE", 18, 100)
    ge_df.expect_column_to_exist("default.payment.next.month")
    ge_df.expect_column_values_to_be_in_set("default.payment.next.month", [0, 1])
    result = ge_df.validate()

    if not result.get("success", True):
        print("Валидация не пройдена:", result)
        sys.exit(1)
    print("Валидация Great Expectations пройдена")


if __name__ == "__main__":
    main()
