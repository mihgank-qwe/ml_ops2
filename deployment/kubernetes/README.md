# Kubernetes манифесты

## Файлы

- `configmap.yaml` - конфигурация (MODEL_PATH, PORT, LOG_LEVEL)
- `secret.yaml` - секреты (заполнить в production)
- `deployment.yaml` - Deployment со стратегией rolling update
- `service.yaml` - Service
- `ingress.yaml` - Ingress

## Применение

```bash
# Заменить image на ваш registry
# В deployment.yaml: image: your-registry/credit-scoring-api:latest

kubectl apply -f deployment/kubernetes/
```

## Rolling update

Стратегия: `maxSurge: 1`, `maxUnavailable: 0` — по одному поду обновляется за раз.
