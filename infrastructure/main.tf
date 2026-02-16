terraform {
  required_version = ">= 1.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
}

provider "yandex" {
  zone      = var.zone
  cloud_id  = var.yandex_cloud_id
  folder_id = var.yandex_folder_id
}

module "vpc" {
  source = "./modules/vpc"

  environment = var.environment
  zone        = var.zone
}

module "storage" {
  source = "./modules/storage"

  environment = var.environment
}

module "kubernetes" {
  source = "./modules/kubernetes"

  environment            = var.environment
  folder_id              = var.yandex_folder_id
  network_id             = module.vpc.network_id
  subnet_id              = module.vpc.subnet_id
  zone                   = var.zone
  master_security_groups = [module.vpc.k8s_security_group_id]
  enable_gpu_nodes       = var.enable_gpu_nodes
  gpu_cluster_id         = var.gpu_cluster_id
}

module "monitoring" {
  source = "./modules/monitoring"

  environment = var.environment
}
