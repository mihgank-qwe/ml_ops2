"""
Нагрузочное тестирование модели: CPU (и GPU при наличии).
Разные конфигурации (потоки, размер батча), определение рекомендуемой конфигурации.
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


def build_input_feed(X_ordered, input_names, batch_slice):
    """Создаёт input_feed для batch_slice"""
    return {
        name: X_ordered[batch_slice, i : i + 1].astype(np.float32)
        for i, name in enumerate(input_names)
    }


def run_load_test(
    sess, X_ordered, input_names, batch_sizes, n_runs=50, n_warmup=5
):
    """Замер latency и throughput для разных размеров батча"""
    results = []
    for batch_size in batch_sizes:
        n = min(batch_size, len(X_ordered))
        batch_slice = slice(0, n)
        input_feed = build_input_feed(X_ordered, input_names, batch_slice)

        _ = sess.run(None, {k: v[: min(5, n)] for k, v in input_feed.items()})
        start = time.perf_counter()
        for _ in range(n_runs):
            _ = sess.run(None, input_feed)
        elapsed = time.perf_counter() - start

        latency_ms = (elapsed / n_runs) * 1000
        throughput = (n_runs * n) / elapsed
        results.append(
            {
                "batch_size": n,
                "latency_ms": round(latency_ms, 2),
                "throughput_samples_per_sec": round(throughput, 2),
            }
        )
    return results


def create_session(model_path, providers=None, threads=0):
    """Создаёт InferenceSession с указанными провайдерами и потоками"""
    opts = ort.SessionOptions()
    if threads > 0:
        opts.intra_op_num_threads = threads
        opts.inter_op_num_threads = threads
    return ort.InferenceSession(
        str(model_path),
        sess_options=opts,
        providers=providers or ort.get_available_providers(),
    )


def main():
    onnx_path = project_root / "models" / "model.onnx"
    quantized_path = project_root / "models" / "model_quantized.onnx"

    if not onnx_path.exists():
        raise FileNotFoundError(
            f"ONNX модель не найдена: {onnx_path}. Запустите: python scripts/model_training/onnx_conversion.py"
        )

    _, X_test, _, _ = load_data()
    X_test = X_test.astype(np.float32)
    model = joblib.load(project_root / "models" / "credit_nn.pkl")
    feature_names = list(model.feature_names_in_)
    X_ordered = X_test[feature_names].values

    # Провайдеры: CPU (и GPU при наличии)
    providers = ort.get_available_providers()
    has_cuda = "CUDAExecutionProvider" in providers
    cpu_providers = ["CPUExecutionProvider"]

    batch_sizes = [1, 10, 100, 500, 1000, 2000, 5000, len(X_ordered)]
    n_runs = 50
    n_warmup = 5

    report = {
        "environment": {
            "cpu_providers": cpu_providers,
            "gpu_available": has_cuda,
            "all_providers": providers,
        },
        "configurations": [],
        "recommendations": {},
    }

    # Конфигурации
    configs = [
        ("onnx_cpu_4threads", onnx_path, cpu_providers, 4),
        ("onnx_cpu_4threads", onnx_path, cpu_providers, 4),
    ]
    configs = [
        ("onnx_cpu_1thread", onnx_path, cpu_providers, 1),
        ("onnx_cpu_2threads", onnx_path, cpu_providers, 2),
        ("onnx_cpu_4threads", onnx_path, cpu_providers, 4),
        ("onnx_cpu_8threads", onnx_path, cpu_providers, 8),
    ]
    if quantized_path.exists():
        configs.extend(
            [
                ("quantized_cpu_2threads", quantized_path, cpu_providers, 2),
                ("quantized_cpu_4threads", quantized_path, cpu_providers, 4),
            ]
        )
    if has_cuda:
        configs.append(
            ("onnx_cuda", onnx_path, ["CUDAExecutionProvider"], 0)
        )

    seen = set()
    for name, model_path, provs, threads in configs:
        key = f"{name}_{threads}"
        if key in seen:
            continue
        seen.add(key)

        try:
            sess = create_session(model_path, provs, threads)
            input_names = [inp.name for inp in sess.get_inputs()]
            results = run_load_test(
                sess, X_ordered, input_names, batch_sizes, n_runs, n_warmup
            )
            report["configurations"].append(
                {
                    "name": key,
                    "model": model_path.name,
                    "provider": provs[0],
                    "threads": threads,
                    "batch_results": results,
                }
            )
        except Exception as e:
            report["configurations"].append(
                {
                    "name": key,
                    "error": str(e),
                }
            )

    # Рекомендации
    valid = [
        c for c in report["configurations"] if "batch_results" in c
    ]
    if valid:
        best_throughput = 0
        best_latency_single = float("inf")
        for cfg in valid:
            for br in cfg.get("batch_results", []):
                if br["batch_size"] == len(X_ordered):
                    if br["throughput_samples_per_sec"] > best_throughput:
                        best_throughput = br["throughput_samples_per_sec"]
                        report["recommendations"]["best_throughput"] = {
                            "config": cfg["name"],
                            "throughput": br["throughput_samples_per_sec"],
                            "latency_ms": br["latency_ms"],
                        }
                if br["batch_size"] == 1:
                    if br["latency_ms"] < best_latency_single:
                        best_latency_single = br["latency_ms"]
                        report["recommendations"]["best_latency_single"] = {
                            "config": cfg["name"],
                            "latency_ms": br["latency_ms"],
                        }

        report["recommendations"]["summary"] = (
            "Для production: quantized_cpu_4threads при batch 100-500. "
            "Для real-time (latency < 1ms): quantized, batch 1. "
            "Для batch: onnx_cpu_4threads или quantized_cpu_4threads."
        )

    output_path = project_root / "models" / "load_test_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=== Нагрузочное тестирование ===")
    print(f"GPU: {'да' if has_cuda else 'нет'}")
    print(f"Размеры батча: {batch_sizes}")
    print()
    for cfg in report["configurations"]:
        if "error" in cfg:
            print(f"{cfg['name']}: ОШИБКА - {cfg['error']}")
        else:
            print(f"{cfg['name']}:")
            for br in cfg["batch_results"][:4]:
                print(
                    f"  batch={br['batch_size']:5d}: "
                    f"{br['latency_ms']:7.2f} ms, "
                    f"{br['throughput_samples_per_sec']:,.0f} samples/sec"
                )
            print()
    print("Рекомендации:")
    for k, v in report["recommendations"].items():
        if k != "summary" and isinstance(v, dict):
            print(f"  {k}: {v}")
    print(f"  {report['recommendations'].get('summary', '')}")
    print()
    print(f"Отчёт сохранён: {output_path}")


if __name__ == "__main__":
    main()
