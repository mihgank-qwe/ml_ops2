# Infrastructure as Code (Terraform)

Terraform-конфигурация для развертывания кредитной скоринговой системы в Yandex Cloud.

## Структура

```
infrastructure/
├── main.tf           # Корневой файл, вызов модулей
├── variables.tf      # Переменные
├── outputs.tf        # Выходные значения
├── terraform.tfvars.example
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

1. Скопируйте `terraform.tfvars.example` в `terraform.tfvars`
2. Заполните `yandex_cloud_id` и `yandex_folder_id`
3. Установите переменные окружения или настройте провайдер
4. Выполните:

```bash
cd infrastructure
terraform init
terraform plan
# terraform apply
```

## Модули

- **vpc** — сеть и подсеть 10.0.1.0/24
- **kubernetes** — Managed Kubernetes 1.28, node group (2x2 vCPU, 4 GB)
- **storage** — бакет для state и артефактов
