# Loki + Promtail — централизованное логирование

## Компоненты

- **Loki** — хранилище логов (аналог Elasticsearch для логов)
- **Promtail** — DaemonSet, собирает логи из подов на каждой ноде и отправляет в Loki

## Развёртывание

```bash
# 1. Loki
kubectl apply -f deployment/monitoring/logging/loki-configmap.yaml
kubectl apply -f deployment/monitoring/logging/loki-deployment.yaml

# 2. Promtail (RBAC + DaemonSet)
kubectl apply -f deployment/monitoring/logging/promtail-rbac.yaml
kubectl apply -f deployment/monitoring/logging/promtail-configmap.yaml
kubectl apply -f deployment/monitoring/logging/promtail-daemonset.yaml
```

## Просмотр логов

Grafana => Explore => выбрать datasource **Loki** => LogQL.

Примеры запросов:

- `{namespace="production"}` — логи из production
- `{app="credit-scoring-api"}` — логи API
- `{namespace="staging"} |= "error"` — ошибки в staging

## Конфигурация

| Метрика   | Значение                             |
| --------- | ------------------------------------ |
| Retention | 7 дней                               |
| Хранилище | emptyDir (для production — PVC)      |
| Лейблы    | namespace, pod, container, app, node |

## Альтернатива: ELK

Для развёртывания ELK stack:

```bash
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n monitoring
helm install kibana elastic/kibana -n monitoring
helm install filebeat elastic/filebeat -n monitoring
```

Для production рекомендуется managed-сервисы (OpenSearch, Elastic Cloud).
