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

output "k8s_security_group_id" {
  description = "ID security group для Kubernetes"
  value       = module.vpc.k8s_security_group_id
}

output "monitoring_placeholder" {
  description = "Заглушка мониторинга (расширить в этапе 5)"
  value       = module.monitoring.placeholder
}
