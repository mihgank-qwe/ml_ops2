# Алерты

## Prometheus (метрики)

### Standalone Prometheus

```bash
kubectl apply -f deployment/monitoring/alerts/prometheus-rules.yaml
# Правила подхватываются Prometheus (rule_files в prometheus.yml)
```

### kube-prometheus-stack (Prometheus Operator)

```bash
kubectl apply -f deployment/monitoring/alerts/prometheusrule-credit-scoring.yaml
```

## Правила

| Алерт | Severity | Условие |
|-------|----------|---------|
| CreditScoringAPIDown | critical | up == 0 для credit-scoring-api |
| CreditScoringAPIHighLatency | warning | p99 > 2s |
| CreditScoringAPIHighErrorRate | critical | 5xx > 5% |
| CreditScoringAPIHighMemory | warning | RSS > 450MB |
| TargetDown | critical | Любой target down |
| PrometheusDown | critical | Prometheus недоступен |

## Loki (логи)

Алерты по логам настраиваются в Grafana: Alerting → New alert rule → Loki datasource.

Пример: `count_over_time({app="credit-scoring-api"} |= "error" [5m]) > 10`

## Runbook

См. [docs/runbook.md](../../../docs/runbook.md) — процедуры реагирования на каждый алерт.
