variable "environment" {
  description = "Окружение"
  type        = string
}

variable "folder_id" {
  description = "ID каталога Yandex Cloud"
  type        = string
}

variable "network_id" {
  description = "ID сети VPC"
  type        = string
}

variable "subnet_id" {
  description = "ID подсети"
  type        = string
}

variable "zone" {
  description = "Зона доступности"
  type        = string
}

variable "master_security_groups" {
  description = "Security groups для master нод Kubernetes"
  type        = list(string)
  default     = []
}

variable "enable_gpu_nodes" {
  description = "Создать node group с GPU (если доступно в облаке)"
  type        = bool
  default     = false
}

variable "gpu_cluster_id" {
  description = "ID GPU cluster в Yandex Cloud (нужен для GPU node group)"
  type        = string
  default     = ""
}
