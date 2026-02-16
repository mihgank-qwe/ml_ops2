output "vpc_network_id" {
  description = "ID сети VPC"
  value       = module.vpc.network_id
}

output "vpc_subnet_id" {
  description = "ID подсети"
  value       = module.vpc.subnet_id
}

output "kubernetes_cluster_id" {
  description = "ID кластера Kubernetes"
  value       = module.kubernetes.cluster_id
}

output "storage_bucket_name" {
  description = "Имя бакета Object Storage"
  value       = module.storage.bucket_name
}
