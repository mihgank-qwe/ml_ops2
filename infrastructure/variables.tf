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

variable "enable_gpu_nodes" {
  description = "Создать GPU node group (требуется gpu_cluster_id)"
  type        = bool
  default     = false
}

variable "gpu_cluster_id" {
  description = "ID GPU cluster в Yandex Cloud"
  type        = string
  default     = ""
}

variable "artifacts_bucket_name" {
  description = "Имя бакета для артефактов (модели, данные). Глобально уникальное."
  type        = string
}
