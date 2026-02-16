output "state_bucket_name" {
  description = "Имя бакета для Terraform state"
  value       = yandex_storage_bucket.state.bucket
}

output "access_key" {
  description = "Access key для S3 backend"
  value       = yandex_iam_service_account_static_access_key.storage_key.access_key
  sensitive   = true
}

output "secret_key" {
  description = "Secret key для S3 backend"
  value       = yandex_iam_service_account_static_access_key.storage_key.secret_key
  sensitive   = true
}
