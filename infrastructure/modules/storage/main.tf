# Бакет для артефактов (модели, данные). State bucket создаётся в bootstrap.
resource "yandex_iam_service_account" "artifacts" {
  name        = "storage-artifacts-${var.environment}"
  description = "Service account for artifacts bucket"
  folder_id   = var.folder_id
}

resource "yandex_resourcemanager_folder_iam_member" "artifacts_storage" {
  folder_id = var.folder_id
  role      = "storage.admin"
  member    = "serviceAccount:${yandex_iam_service_account.artifacts.id}"
}

resource "yandex_iam_service_account_static_access_key" "artifacts_key" {
  service_account_id = yandex_iam_service_account.artifacts.id
  description        = "Static key for artifacts bucket"
}

resource "yandex_storage_bucket" "artifacts" {
  bucket     = var.artifacts_bucket_name
  access_key = yandex_iam_service_account_static_access_key.artifacts_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.artifacts_key.secret_key
}
