# Отчёт по бенчмаркам модели кредитного скоринга

---

## 1. Размеры моделей

| Модель                    | Размер   | Описание                         |
| ------------------------- | -------- | -------------------------------- |
| `credit_nn.pkl` (sklearn) | ~0.5 MB  | Исходная NN, pickle              |
| `model.onnx`              | ~0.09 MB | ONNX float32                     |
| `model_quantized.onnx`    | ~0.03 MB | ONNX int8 (dynamic quantization) |

**Сжатие после квантизации:** ~66% (0.09 MB → 0.03 MB)

---

## 2. Сравнение инференса (batch ~6k, CPU)

| Реализация     | Latency (мс) | Throughput (samples/sec) |
| -------------- | ------------ | ------------------------ |
| Sklearn        | ~13–15       | ~444k                    |
| ONNX float32   | ~7–8         | ~833k                    |
| ONNX quantized | ~6–7         | ~906k                    |

**Ускорение ONNX vs Sklearn:** ~1.9x  
**Ускорение Quantized vs ONNX:** ~1.2x

---

## 3. Метрики качества

| Модель             | AUC   | Precision | Recall | F1   |
| ------------------ | ----- | --------- | ------ | ---- |
| Sklearn (baseline) | 0.767 | 0.69      | 0.32   | 0.44 |
| ONNX float32       | 0.767 | —         | —      | —    |
| ONNX quantized     | 0.758 | —         | —      | —    |

**Дельта AUC после квантизации:** −0.009 (допустимо для production)

---

## 4. Нагрузочное тестирование

### Конфигурации (имитация типов инстансов)

| Конфигурация           | Потоки | Batch 1 (мс) | Batch 100 (samples/sec) | Batch 6k (samples/sec) |
| ---------------------- | ------ | ------------ | ----------------------- | ---------------------- |
| onnx_cpu_1thread       | 1      | 0.10         | ~450k                   | ~632k                  |
| onnx_cpu_2threads      | 2      | 0.12         | ~433k                   | ~941k                  |
| onnx_cpu_4threads      | 4      | 0.11         | ~461k                   | **~1.17M**             |
| onnx_cpu_8threads      | 8      | 0.10         | ~418k                   | ~946k                  |
| quantized_cpu_2threads | 2      | 0.11         | ~461k                   | ~936k                  |
| quantized_cpu_4threads | 4      | 0.11         | ~455k                   | ~1.06M                 |

### Лучшие результаты

- **Минимальная latency (batch=1):** 0.10 мс (onnx_cpu_1thread)
- **Максимальный throughput (batch=6k):** ~1.17M samples/sec (onnx_cpu_4threads)

---

## 5. Рекомендации по ресурсам

### Production (batch 100–500)

- **Конфигурация:** `quantized_cpu_4threads` или `onnx_cpu_4threads`
- **Ресурсы:** 4 vCPU, 2–4 GB RAM
- **Модель:** `model_quantized.onnx` (меньше размер, сопоставимая скорость)
- **Ожидаемый throughput:** 800k–1M samples/sec

### Real-time API (batch=1, latency < 1 мс)

- **Конфигурация:** `onnx_cpu_1thread` или `quantized_cpu_2threads`
- **Ресурсы:** 1–2 vCPU, 1 GB RAM
- **Ожидаемая latency:** ~0.1 мс на запрос

### Batch-обработка (максимальный throughput)

- **Конфигурация:** `onnx_cpu_4threads`
- **Ресурсы:** 4 vCPU, 4 GB RAM
- **Batch size:** 1000–6000
- **Ожидаемый throughput:** >1M samples/sec

### GPU

- GPU не требуется: модель небольшая, CPU справляется с запасом.
- При росте нагрузки рассмотреть GPU для батчей >10k.

---

## 6. Скрипты для воспроизведения

```bash
# Обучение NN
python scripts/model_training/train_nn.py

# Конвертация в ONNX
python scripts/model_training/onnx_conversion.py

# Валидация конвертации
python scripts/model_training/validate_onnx.py

# Бенчмарк sklearn vs ONNX
python scripts/model_training/benchmark_inference.py

# Квантизация
python scripts/model_training/optimize_model.py

# Нагрузочное тестирование
python scripts/model_training/load_test.py
```

---

## 7. Исходные данные бенчмарков

- `models/benchmark_results.json` — sklearn vs ONNX
- `models/optimization_report.json` — до/после квантизации
- `models/load_test_report.json` — нагрузочные тесты по конфигурациям
