"""
Сравнение производительности инференса: исходная модель (sklearn) vs ONNX на CPU.
Замер времени и throughput, запись результатов в models/benchmark_results.json.
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

from src.models.train import load_data


def benchmark_sklearn(model, X, n_warmup=10, n_runs=100):
    """Прогрев и замер времени sklearn predict_proba."""
    _ = model.predict_proba(X[:n_warmup])
    start = time.perf_counter()
    for _ in range(n_runs):
        _ = model.predict_proba(X)
    elapsed = time.perf_counter() - start
    return elapsed / n_runs, n_runs / elapsed * len(X)


def benchmark_onnx(sess, input_feed, n_samples, n_warmup=10, n_runs=100):
    """Прогрев и замер времени ONNX inference."""
    _ = sess.run(None, {k: v[:n_warmup] for k, v in input_feed.items()})
    start = time.perf_counter()
    for _ in range(n_runs):
        _ = sess.run(None, input_feed)
    elapsed = time.perf_counter() - start
    return elapsed / n_runs, n_runs / elapsed * n_samples


def main():
    model_path = project_root / "models" / "credit_nn.pkl"
    onnx_path = project_root / "models" / "model.onnx"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}. Запустите: python scripts/model_training/train_nn.py"
        )
    if not onnx_path.exists():
        raise FileNotFoundError(
            f"ONNX модель не найдена: {onnx_path}. Запустите: python scripts/model_training/onnx_conversion.py"
        )

    _, X_test, _, _ = load_data()
    X_test = X_test.astype(np.float32)
    n_samples = len(X_test)

    model = joblib.load(model_path)
    feature_names = list(model.feature_names_in_)
    X_ordered = X_test[feature_names].values

    # ONNX session
    sess = ort.InferenceSession(str(onnx_path))
    input_names = [inp.name for inp in sess.get_inputs()]
    input_feed = {
        name: X_ordered[:, i : i + 1].astype(np.float32)
        for i, name in enumerate(input_names)
    }

    n_warmup = 10
    n_runs = 100

    # Бенчмарк sklearn
    latency_sklearn, throughput_sklearn = benchmark_sklearn(
        model, X_test, n_warmup=n_warmup, n_runs=n_runs
    )

    # Бенчмарк ONNX
    latency_onnx, throughput_onnx = benchmark_onnx(
        sess, input_feed, n_samples, n_warmup=n_warmup, n_runs=n_runs
    )

    results = {
        "n_samples": n_samples,
        "n_warmup": n_warmup,
        "n_runs": n_runs,
        "sklearn": {
            "latency_ms": round(latency_sklearn * 1000, 4),
            "throughput_samples_per_sec": round(throughput_sklearn, 2),
        },
        "onnx": {
            "latency_ms": round(latency_onnx * 1000, 4),
            "throughput_samples_per_sec": round(throughput_onnx, 2),
        },
        "speedup": round(throughput_onnx / throughput_sklearn, 2),
    }

    output_path = project_root / "models" / "benchmark_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=== Сравнение производительности инференса (CPU) ===")
    print(f"Примеров: {n_samples}, прогонов: {n_runs}")
    print()
    print("Sklearn:")
    print(f"  Latency: {results['sklearn']['latency_ms']} ms")
    print(f"  Throughput: {results['sklearn']['throughput_samples_per_sec']} samples/sec")
    print()
    print("ONNX:")
    print(f"  Latency: {results['onnx']['latency_ms']} ms")
    print(f"  Throughput: {results['onnx']['throughput_samples_per_sec']} samples/sec")
    print()
    print(f"Ускорение ONNX vs sklearn: {results['speedup']}x")
    print(f"Результаты сохранены: {output_path}")


if __name__ == "__main__":
    main()
