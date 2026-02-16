# Prometheus + Grafana — мониторинг

## Метрики приложения

Credit Scoring API экспортирует метрики на `/metrics`:
- **HTTP**: `http_requests_total`, `http_request_duration_seconds` (prometheus-fastapi-instrumentator)
- **Process**: `process_cpu_seconds_total`, `process_resident_memory_bytes` (prometheus_client)

## Развёртывание

### Вариант 1: Standalone (Prometheus + Grafana)

```bash
# 1. Namespace, Prometheus, RBAC, алерты
kubectl apply -f deployment/monitoring/namespace.yaml
kubectl apply -f deployment/monitoring/prometheus-configmap.yaml
kubectl apply -f deployment/monitoring/prometheus-rbac.yaml
kubectl apply -f deployment/monitoring/alerts/prometheus-rules.yaml
kubectl apply -f deployment/monitoring/prometheus-deployment.yaml

# 2. Grafana: дашборды из JSON в репозитории
cd deployment/monitoring && make dashboards && cd ../..

# 3. Grafana deployment
kubectl apply -f deployment/monitoring/grafana-datasource.yaml
kubectl apply -f deployment/monitoring/grafana-provisioning.yaml
kubectl apply -f deployment/monitoring/grafana-deployment.yaml
```

### Вариант 2: kube-prometheus-stack (Helm)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -f deployment/monitoring/servicemonitor-credit-scoring.yaml
# Импорт дашбордов: Grafana UI → Dashboards → Import → загрузить JSON из dashboards/
```

## Дашборды Grafana

| Файл | Описание |
|------|----------|
| `dashboards/api-dashboard.json` | Credit Scoring API: RPS, latency (p50/p99), memory, CPU |
| `dashboards/infrastructure-dashboard.json` | K8s: nodes, pods, containers, targets health |

Панели:
- **API**: Request Rate, Latency, Requests by Status, Memory, CPU
- **Infrastructure**: Node CPU/Memory, Container CPU/Memory, Targets Health

*Примечание:* Node CPU/Memory требуют node_exporter (входит в kube-prometheus-stack). Container metrics — из kubelet.

## Алерты и Runbook

- **Правила:** `deployment/monitoring/alerts/` — Prometheus alert rules
- **Runbook:** [docs/runbook.md](../docs/runbook.md) — процедуры реагирования на инциденты

## Логирование (Loki + Promtail)

Централизованный сбор логов: `deployment/monitoring/logging/`. См. [logging/README.md](logging/README.md).

## Scrape targets

| Job | Описание |
|-----|----------|
| prometheus | Self-monitoring |
| credit-scoring-api | Метрики API (requests, latency) |
| kubernetes-apiservers | Метрики API server |
| kubernetes-nodes | Метрики нод (kubelet) |
| kubernetes-pods | Поды с аннотацией prometheus.io/scrape |
| kubernetes-service-endpoints | Endpoints с аннотацией |
