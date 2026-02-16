"""
Оптимизация модели: quantization ONNX.
Замер размера, скорости и метрик до/после, запись отчёта в models/optimization_report.json.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import onnxruntime as ort
from onnxruntime.quantization import QuantType, quantize_dynamic

from src.models.train import load_data
from sklearn.metrics import roc_auc_score


def get_file_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def benchmark_onnx(sess, input_feed, n_samples, n_warmup=10, n_runs=100):
    _ = sess.run(None, {k: v[:n_warmup] for k, v in input_feed.items()})
    start = time.perf_counter()
    for _ in range(n_runs):
        _ = sess.run(None, input_feed)
    elapsed = time.perf_counter() - start
    return elapsed / n_runs, n_runs / elapsed * n_samples


def get_proba_from_onnx(sess, input_feed):
    _, proba_output = sess.run(["output_label", "output_probability"], input_feed)
    return np.array([p[1] for p in proba_output], dtype=np.float32)


def main():
    onnx_path = project_root / "models" / "model.onnx"
    quantized_path = project_root / "models" / "model_quantized.onnx"
    sklearn_path = project_root / "models" / "credit_nn.pkl"

    if not onnx_path.exists():
        raise FileNotFoundError(
            f"ONNX модель не найдена: {onnx_path}. Запустите: python scripts/model_training/onnx_conversion.py"
        )

    _, X_test, _, y_test = load_data()
    X_test = X_test.astype(np.float32)
    n_samples = len(X_test)

    # Загрузка sklearn для порядка признаков
    model_sklearn = joblib.load(sklearn_path)
    feature_names = list(model_sklearn.feature_names_in_)
    X_ordered = X_test[feature_names].values

    sess_orig = ort.InferenceSession(str(onnx_path))
    input_names = [inp.name for inp in sess_orig.get_inputs()]
    input_feed = {
        name: X_ordered[:, i : i + 1].astype(np.float32)
        for i, name in enumerate(input_names)
    }

    # Размер и метрики ДО
    size_before_mb = get_file_size_mb(onnx_path)
    proba_before = get_proba_from_onnx(sess_orig, input_feed)
    auc_before = roc_auc_score(y_test, proba_before)
    latency_before, throughput_before = benchmark_onnx(
        sess_orig, input_feed, n_samples
    )

    # Квантизация
    quantize_dynamic(
        model_input=str(onnx_path),
        model_output=str(quantized_path),
        weight_type=QuantType.QInt8,
        per_channel=False,
        reduce_range=False,
    )

    # Размер и метрики ПОСЛЕ
    size_after_mb = get_file_size_mb(quantized_path)
    sess_quant = ort.InferenceSession(str(quantized_path))
    proba_after = get_proba_from_onnx(sess_quant, input_feed)
    auc_after = roc_auc_score(y_test, proba_after)
    latency_after, throughput_after = benchmark_onnx(
        sess_quant, input_feed, n_samples
    )

    # Отчёт
    report = {
        "optimization": "dynamic_quantization_int8",
        "before": {
            "model_path": str(onnx_path),
            "size_mb": round(size_before_mb, 4),
            "latency_ms": round(latency_before * 1000, 4),
            "throughput_samples_per_sec": round(throughput_before, 2),
            "auc": round(auc_before, 4),
        },
        "after": {
            "model_path": str(quantized_path),
            "size_mb": round(size_after_mb, 4),
            "latency_ms": round(latency_after * 1000, 4),
            "throughput_samples_per_sec": round(throughput_after, 2),
            "auc": round(auc_after, 4),
        },
        "delta": {
            "size_reduction_percent": round(
                (1 - size_after_mb / size_before_mb) * 100, 2
            ),
            "speedup": round(throughput_after / throughput_before, 2),
            "auc_diff": round(auc_after - auc_before, 4),
        },
    }

    output_path = project_root / "models" / "optimization_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=== Оптимизация модели (Quantization) ===")
    print()
    print("ДО оптимизации:")
    print(f"  Размер: {report['before']['size_mb']} MB")
    print(f"  Latency: {report['before']['latency_ms']} ms")
    print(f"  Throughput: {report['before']['throughput_samples_per_sec']} samples/sec")
    print(f"  AUC: {report['before']['auc']}")
    print()
    print("ПОСЛЕ оптимизации (int8 dynamic quantization):")
    print(f"  Размер: {report['after']['size_mb']} MB")
    print(f"  Latency: {report['after']['latency_ms']} ms")
    print(f"  Throughput: {report['after']['throughput_samples_per_sec']} samples/sec")
    print(f"  AUC: {report['after']['auc']}")
    print()
    print("Изменения:")
    print(f"  Сжатие: {report['delta']['size_reduction_percent']}%")
    print(f"  Ускорение: {report['delta']['speedup']}x")
    print(f"  Delta AUC: {report['delta']['auc_diff']:+.4f}")
    print()
    print(f"Квантизированная модель: {quantized_path}")
    print(f"Отчёт сохранён: {output_path}")


if __name__ == "__main__":
    main()
