# Infrastructure as Code (Terraform)

Terraform-конфигурация для развертывания кредитной скоринговой системы в Yandex Cloud.

## Требования

- Terraform >= 1.0
- Yandex Cloud: cloud_id, folder_id
- Аутентификация: `YC_TOKEN` или `YC_SERVICE_ACCOUNT_KEY_FILE`

## Структура

```
infrastructure/
├── main.tf              # Корневой файл, вызов модулей
├── variables.tf         # Переменные
├── outputs.tf           # Выходные значения
├── backend.tf           # Remote state в Object Storage
├── backend-config.example.hcl
├── terraform.tfvars.example
├── bootstrap/           # Создание state bucket (запустить первым)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
└── modules/
    ├── vpc/          # Сеть, подсети, security groups
    ├── kubernetes/   # Managed Kubernetes, node group
    ├── storage/      # Object Storage (артефакты)
    └── monitoring/  # Заготовка под Prometheus/Grafana
```

---

## Инициализация Terraform

### Bootstrap (первый запуск)

```bash
cd infrastructure/bootstrap
terraform init
```

State bootstrap хранится **локально** (`terraform.tfstate` в `bootstrap/`).

### Основная инфраструктура

**Вариант A — с remote state (рекомендуется):**

```bash
cd infrastructure
terraform init -backend-config=backend-config.hcl
```

**Вариант B — без remote state (для первого прогона или тестов):**

```bash
terraform init -backend=false
# После bootstrap: terraform init -backend-config=backend-config.hcl -migrate-state
```

---

## Задание переменных

### 1. terraform.tfvars (рекомендуется)

```bash
cp terraform.tfvars.example terraform.tfvars
# Отредактируйте terraform.tfvars
```

Файл `terraform.tfvars`

### 2. Переменные окружения

```bash
export TF_VAR_yandex_cloud_id="your-cloud-id"
export TF_VAR_yandex_folder_id="your-folder-id"
export TF_VAR_artifacts_bucket_name="your-unique-bucket"
```

### 3. Флаг -var

```bash
terraform plan -var="yandex_cloud_id=xxx" -var="yandex_folder_id=yyy"
```

### Обязательные переменные

| Переменная              | Описание                                         |
| ----------------------- | ------------------------------------------------ |
| `yandex_cloud_id`       | ID облака Yandex Cloud                           |
| `yandex_folder_id`      | ID каталога                                      |
| `artifacts_bucket_name` | Имя бакета для артефактов (глобально уникальное) |

### Bootstrap — переменные

| Переменная          | Описание                                    |
| ------------------- | ------------------------------------------- |
| `state_bucket_name` | Имя бакета для state (глобально уникальное) |

---

## Хранение state

### Bootstrap

- **Где:** локально в `bootstrap/terraform.tfstate`
- **Backend:** `local`

### Основная инфраструктура

- **Где:** Yandex Object Storage (S3-совместимый)
- **Endpoint:** `storage.yandexcloud.net`
- **Путь в бакете:** `infrastructure/terraform.tfstate` (настраивается в backend-config.hcl)
- **Backend:** `s3`

### Настройка remote state

1. Запустите bootstrap, получите `access_key`, `secret_key`, `state_bucket_name`
2. Скопируйте `backend-config.example.hcl` в `backend-config.hcl`
3. Заполните `bucket`, `access_key`, `secret_key`, `key`
4. Выполните: `terraform init -backend-config=backend-config.hcl`

Файл `backend-config.hcl`

---

## Использование

### 1. Bootstrap (создание state bucket)

```bash
cd infrastructure/bootstrap
cp terraform.tfvars.example terraform.tfvars
# Заполните: yandex_cloud_id, yandex_folder_id, state_bucket_name
terraform init
terraform apply
terraform output  # сохраните access_key, secret_key, state_bucket_name
```

### 2. Настройка remote state

```bash
cd ..  # в infrastructure/
cp backend-config.example.hcl backend-config.hcl
# Заполните bucket, access_key, secret_key, key из вывода bootstrap
```

### 3. Основная инфраструктура

```bash
cp terraform.tfvars.example terraform.tfvars
# Заполните переменные
terraform init -backend-config=backend-config.hcl
terraform plan
terraform apply
```

---

## Модули

- **vpc** — сеть, подсеть 10.0.1.0/24, security groups (K8s API 6443, HTTP/HTTPS, API 8000)
- **kubernetes** — Managed Kubernetes 1.28, CPU node group (4 vCPU, 8 GB) с auto_scale 2–10, preemptible для non-production; опционально GPU node group
- **storage** — бакет для артефактов (модели, данные). State bucket создаётся в bootstrap.
- **monitoring** — заготовка (folder_id, cluster_id для этапа 5: Prometheus, Grafana, алерты)
