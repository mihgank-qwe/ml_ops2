output "bucket_name" {
  description = "Имя бакета для артефактов"
  value       = yandex_storage_bucket.artifacts.bucket
}
