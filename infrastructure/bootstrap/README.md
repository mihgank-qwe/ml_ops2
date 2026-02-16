# Bootstrap — создание state bucket

Запустите **первым**, до основной инфраструктуры.

Создаёт:
- Service account для Object Storage
- Бакет для Terraform state
- Static access key

## Использование

```bash
cp terraform.tfvars.example terraform.tfvars
# Заполните: yandex_cloud_id, yandex_folder_id, state_bucket_name
terraform init
terraform apply
terraform output -json  # сохраните access_key, secret_key, state_bucket_name
```

Имя бакета (`state_bucket_name`) должно быть **глобально уникальным** в Yandex Cloud (например: `my-org-credit-scoring-tfstate`).
