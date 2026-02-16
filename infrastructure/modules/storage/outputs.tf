output "bucket_name" {
  description = "Имя бакета Object Storage"
  value       = yandex_storage_bucket.state.bucket
}
