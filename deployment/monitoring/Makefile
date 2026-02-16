# Создание ConfigMap с дашбордами Grafana из JSON-файлов
.PHONY: dashboards
dashboards:
	kubectl create configmap grafana-dashboards \
		--from-file=api-dashboard.json=dashboards/api-dashboard.json \
		--from-file=infrastructure-dashboard.json=dashboards/infrastructure-dashboard.json \
		-n monitoring \
		--dry-run=client -o yaml | kubectl apply -f -
