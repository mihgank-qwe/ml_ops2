variable "environment" {
  description = "Окружение"
  type        = string
  default     = "staging"
}

variable "yandex_cloud_id" {
  description = "ID облака Yandex Cloud"
  type        = string
}

variable "yandex_folder_id" {
  description = "ID каталога Yandex Cloud"
  type        = string
}

variable "state_bucket_name" {
  description = "Имя бакета для Terraform state (глобально уникальное)"
  type        = string
}
