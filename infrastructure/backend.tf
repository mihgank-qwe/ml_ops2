# Remote state в Yandex Object Storage (S3-совместимый).
# 1. Запустите bootstrap: cd bootstrap && terraform apply
# 2. Скопируйте backend-config.example.hcl в backend-config.hcl, заполните из terraform output
# 3. terraform init -backend-config=backend-config.hcl
# 4. При миграции с local: terraform init -backend-config=backend-config.hcl -migrate-state

terraform {
  backend "s3" {
    endpoint                    = "storage.yandexcloud.net"
    region                      = "ru-central1"
    skip_region_validation      = true
    skip_credentials_validation = true
    # bucket, key, access_key, secret_key — через -backend-config=backend-config.hcl
  }
}
