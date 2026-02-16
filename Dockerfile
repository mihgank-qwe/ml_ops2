# ========== Build stage ==========
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ========== DVC stage ==========
FROM python:3.10-slim AS dvc

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir dvc[s3]

COPY . .

# dvc pull — при отсутствии remote команда завершится с ошибкой, продолжаем сборку
RUN dvc pull -R 2>/dev/null || echo "DVC pull skipped (no remote or already cached)"

# ========== Final stage ==========
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY --from=dvc /app/models ./models
COPY --from=dvc /app/data ./data
COPY --from=dvc /app/src ./src

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
