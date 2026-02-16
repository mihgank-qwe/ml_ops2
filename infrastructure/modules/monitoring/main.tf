# Модуль мониторинга — заготовка для этапа 5.
#
# Варианты развёртывания:
# 1. Yandex Monitoring (managed) — метрики из Compute, K8s собираются автоматически.
#    Дашборды: консоль Yandex Cloud => Monitoring.
# 2. Prometheus + Grafana в Kubernetes — helm install prometheus-community/kube-prometheus-stack.
# 3. Managed Service for Prometheus (если доступен в провайдере).
#
# Для этапа 5 добавить:
# - Prometheus: ServiceMonitor, ConfigMap с scrape configs
# - Grafana: Deployment, ConfigMap с дашбордами
# - Алерты: PrometheusRule / Alertmanager
# - Логи: Loki или Cloud Logging
#
# Yandex Monitoring использует folder_id — метрики доступны по умолчанию.

locals {
  monitoring_placeholder = {
    environment = var.environment
    folder_id   = var.folder_id
    cluster_id  = var.cluster_id
    next_steps  = "Этап 5: Prometheus, Grafana, алерты, runbook"
  }
}
