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
