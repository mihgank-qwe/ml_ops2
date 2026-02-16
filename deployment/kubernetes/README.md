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

**Security scanning:** Trivy (vulnerability scan) и Dockle (best practices) — образ проверяется до push. Исключения: `.trivyignore`.

### Окружения

| Окружение | Триггер | Namespace |
|-----------|---------|-----------|
| **Staging** | push в `develop`, теги `v*` | staging |
| **Production** | push в `main` | production |

Для каждого окружения создать GitHub Environment (Settings → Environments) с отдельными секретами.

### Аутентификация

**Вариант 1 — KUBECONFIG (по умолчанию):**
- Секрет `KUBECONFIG` — содержимое kubeconfig (разные значения для staging/production)

**Вариант 2 — Yandex Cloud:**
- Variable `AUTH_METHOD` = `yandex`
- Variable `YANDEX_CLUSTER_ID` — ID кластера (разные для staging/production)
- Секрет `YANDEX_SERVICE_ACCOUNT_KEY` — JSON-ключ service account

**Ingress:** Variable `INGRESS_HOST` — домен для Ingress (например credit-scoring-staging.example.com / credit-scoring.example.com)

## Rolling update

Стратегия: `maxSurge: 1`, `maxUnavailable: 0` — по одному поду обновляется за раз.
