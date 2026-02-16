variable "environment" {
  description = "Окружение"
  type        = string
}

variable "folder_id" {
  description = "ID каталога Yandex Cloud"
  type        = string
}

variable "artifacts_bucket_name" {
  description = "Имя бакета для артефактов (модели, данные). Глобально уникальное."
  type        = string
}
