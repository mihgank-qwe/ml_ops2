resource "yandex_storage_bucket" "state" {
  bucket     = "credit-scoring-${var.environment}-state"
  access_key = null
  secret_key = null
}
