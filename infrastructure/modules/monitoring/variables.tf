variable "environment" {
  description = "Окружение"
  type        = string
}

variable "folder_id" {
  description = "ID каталога (для Yandex Monitoring)"
  type        = string
  default     = ""
}

variable "cluster_id" {
  description = "ID кластера Kubernetes (для Prometheus scrape targets)"
  type        = string
  default     = ""
}
