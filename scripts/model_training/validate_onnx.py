"""
Валидация конвертации ONNX: сравнение предсказаний исходной модели и ONNX
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import onnxruntime as ort

from src.models.train import TARGET_COL, load_data


def main():
    model_path = project_root / "models" / "credit_nn.pkl"
    onnx_path = project_root / "models" / "model.onnx"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}. Запустите python scripts/model_training/train_nn.py"
        )
    if not onnx_path.exists():
        raise FileNotFoundError(
            f"ONNX модель не найдена: {onnx_path}. Запустите python scripts/model_training/onnx_conversion.py"
        )

    # Загрузка данных
    _, X_test, _, _ = load_data()
    X_test = X_test.astype(np.float32)

    model = joblib.load(model_path)
    feature_names = list(model.feature_names_in_)
    X_ordered = X_test[feature_names].values

    # Предсказания исходной модели
    pred_sklearn = model.predict(X_test)
    proba_sklearn = model.predict_proba(X_test)[:, 1]

    # Предсказания ONNX
    sess = ort.InferenceSession(str(onnx_path))
    input_names = [inp.name for inp in sess.get_inputs()]

    input_feed = {
        name: X_ordered[:, i : i + 1].astype(np.float32)
        for i, name in enumerate(input_names)
    }
    pred_onnx, proba_output = sess.run(
        ["output_label", "output_probability"], input_feed
    )

    # output_probability
    proba_onnx = np.array([p[1] for p in proba_output], dtype=np.float32)

    # Сравнение
    labels_match = np.allclose(pred_sklearn, pred_onnx)
    proba_diff = np.abs(proba_sklearn - proba_onnx)
    max_proba_diff = np.max(proba_diff)
    mean_proba_diff = np.mean(proba_diff)

    print("=== Валидация конвертации ONNX ===")
    print(f"Примеров: {len(X_test)}")
    print(f"Совпадение меток (0/1): {'OK' if labels_match else 'ОШИБКА'}")
    print(f"Макс. разница вероятностей: {max_proba_diff:.6f}")
    print(f"Средняя разница вероятностей: {mean_proba_diff:.6f}")

    if labels_match and max_proba_diff < 1e-4:
        print("\nКонвертация корректна: предсказания совпадают")
    elif labels_match:
        print("\nКонвертация корректна: метки совпадают, небольшие отличия в вероятностях")
    else:
        n_mismatch = np.sum(pred_sklearn != pred_onnx)
        print(f"\nВНИМАНИЕ: расхождение в {n_mismatch} из {len(X_test)} предсказаний")


if __name__ == "__main__":
    main()
