# Kubernetes манифесты

## Файлы

- `configmap.yaml` - конфигурация (MODEL_PATH, PORT, LOG_LEVEL)
- `secret.yaml` - секреты (заполнить в production)
- `deployment.yaml` - Deployment со стратегией rolling update
- `service.yaml` - Service (ClusterIP, порт 8000)
- `ingress.yaml` - Ingress (host: credit-scoring.example.com, заменить на свой домен)

## Применение

```bash
kubectl apply -f deployment/kubernetes/
```

При ручном применении замените `image` в deployment.yaml на ваш registry.

## CI/CD

При push в main/master GitHub Actions автоматически:
1. Собирает образ и пушит в ghcr.io
2. Обновляет image в deployment.yaml
3. Применяет манифесты в кластер

**Секреты для deploy:** `KUBECONFIG` — содержимое kubeconfig для доступа к кластеру.

## Rolling update

Стратегия: `maxSurge: 1`, `maxUnavailable: 0` — по одному поду обновляется за раз.
