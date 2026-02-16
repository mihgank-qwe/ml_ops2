# Bootstrap: создаёт бакет для Terraform state и ключи доступа.
# Запустить ПЕРВЫМ с local backend, затем использовать в основной конфигурации.
# cd bootstrap && terraform init && terraform apply

terraform {
  required_version = ">= 1.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
  backend "local" {}
}

provider "yandex" {
  cloud_id  = var.yandex_cloud_id
  folder_id = var.yandex_folder_id
}

resource "yandex_iam_service_account" "storage" {
  name        = "storage-${var.environment}"
  description = "Service account for Object Storage"
  folder_id   = var.yandex_folder_id
}

resource "yandex_resourcemanager_folder_iam_member" "storage_admin" {
  folder_id = var.yandex_folder_id
  role      = "storage.admin"
  member    = "serviceAccount:${yandex_iam_service_account.storage.id}"
}

resource "yandex_iam_service_account_static_access_key" "storage_key" {
  service_account_id = yandex_iam_service_account.storage.id
  description        = "Static key for Terraform state bucket"
}

resource "yandex_storage_bucket" "state" {
  bucket     = var.state_bucket_name
  access_key = yandex_iam_service_account_static_access_key.storage_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.storage_key.secret_key
}
