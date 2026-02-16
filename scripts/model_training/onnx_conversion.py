"""
Конвертация обученной NN-модели (sklearn Pipeline с MLPClassifier) в ONNX.
Загружает models/credit_nn.pkl и сохраняет models/model.onnx.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

def main():
    model_path = project_root / "models" / "credit_nn.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}. Сначала запустите: python scripts/model_training/train_nn.py"
        )

    # Загрузка обученной модели
    model = joblib.load(model_path)

    feature_names = list(model.feature_names_in_)
    initial_type = [
        (name, FloatTensorType([None, 1])) for name in feature_names
    ]

    # Конвертация в ONNX
    onx = convert_sklearn(model, initial_types=initial_type)

    # Сохранение ONNX модели
    onnx_path = project_root / "models" / "model.onnx"
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())

    print(f"ONNX модель сохранена: {onnx_path}")
    print(f"Входных признаков: {len(feature_names)}")


if __name__ == "__main__":
    main()
