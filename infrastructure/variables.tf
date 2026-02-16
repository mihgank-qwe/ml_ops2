variable "environment" {
  description = "Окружение (staging, production)"
  type        = string
  default     = "staging"
}

variable "zone" {
  description = "Зона доступности Yandex Cloud"
  type        = string
  default     = "ru-central1-a"
}

variable "yandex_cloud_id" {
  description = "ID облака Yandex Cloud"
  type        = string
}

variable "yandex_folder_id" {
  description = "ID каталога Yandex Cloud"
  type        = string
}
