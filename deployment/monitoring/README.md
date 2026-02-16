# Prometheus — мониторинг

## Метрики приложения

Credit Scoring API экспортирует метрики на `/metrics`:
- **HTTP**: `http_requests_total`, `http_request_duration_seconds` (prometheus-fastapi-instrumentator)
- **Process**: `process_cpu_seconds_total`, `process_resident_memory_bytes` (prometheus_client)

## Развёртывание

### Вариант 1: Standalone Prometheus

```bash
kubectl apply -f deployment/monitoring/
```

Создаётся:
- namespace `monitoring`
- ConfigMap с scrape configs (app, K8s nodes, pods)
- RBAC для доступа к метрикам кластера
- Deployment + Service Prometheus

### Вариант 2: kube-prometheus-stack (Helm)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -f deployment/monitoring/servicemonitor-credit-scoring.yaml
```

## Scrape targets

| Job | Описание |
|-----|----------|
| prometheus | Self-monitoring |
| credit-scoring-api | Метрики API (requests, latency) |
| kubernetes-apiservers | Метрики API server |
| kubernetes-nodes | Метрики нод (kubelet) |
| kubernetes-pods | Поды с аннотацией prometheus.io/scrape |
| kubernetes-service-endpoints | Endpoints с аннотацией |
