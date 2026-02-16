# Infrastructure as Code (Terraform)

Terraform-конфигурация для развертывания кредитной скоринговой системы в Yandex Cloud.

## Структура

```
infrastructure/
├── main.tf              # Корневой файл, вызов модулей
├── variables.tf          # Переменные
├── outputs.tf           # Выходные значения
├── backend.tf           # Remote state в Object Storage
├── backend-config.example.hcl
├── terraform.tfvars.example
├── bootstrap/            # Создание state bucket (запустить первым)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
└── modules/
    ├── vpc/          # Сеть, подсети
    ├── kubernetes/   # Managed Kubernetes, node group
    ├── storage/      # Object Storage (бакет)
    └── monitoring/   # Заготовка под Prometheus/Grafana
```

## Требования

- Terraform >= 1.0
- Yandex Cloud: cloud_id, folder_id
- Аутентификация: `YC_TOKEN` или `YC_SERVICE_ACCOUNT_KEY_FILE`

## Использование

### 1. Bootstrap (создание state bucket)

```bash
cd infrastructure/bootstrap
cp terraform.tfvars.example terraform.tfvars
# Заполните yandex_cloud_id, yandex_folder_id, state_bucket_name (глобально уникальное)
terraform init
terraform apply
terraform output  # сохраните access_key, secret_key, state_bucket_name
```

### 2. Настройка remote state

```bash
cd ..  # в infrastructure/
cp backend-config.example.hcl backend-config.hcl
# Заполните bucket, access_key, secret_key из вывода bootstrap
```

### 3. Основная инфраструктура

```bash
cp terraform.tfvars.example terraform.tfvars
# Заполните переменные, включая artifacts_bucket_name
terraform init -backend-config=backend-config.hcl
# При миграции с local: добавьте -migrate-state
terraform plan
terraform apply
```

## Модули

- **vpc** — сеть, подсеть 10.0.1.0/24, security groups (K8s API 6443, HTTP/HTTPS, API 8000)
- **kubernetes** — Managed Kubernetes 1.28, CPU node group (4 vCPU, 8 GB) с auto_scale 2–10, preemptible для non-production; опционально GPU node group
- **storage** — бакет для артефактов (модели, данные). State bucket создаётся в bootstrap.
- **monitoring** — заготовка (folder_id, cluster_id для этапа 5: Prometheus, Grafana, алерты)
