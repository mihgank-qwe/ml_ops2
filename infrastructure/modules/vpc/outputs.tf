output "network_id" {
  description = "ID сети VPC"
  value       = yandex_vpc_network.main.id
}

output "subnet_id" {
  description = "ID подсети"
  value       = yandex_vpc_subnet.main.id
}

output "k8s_security_group_id" {
  description = "ID security group для Kubernetes"
  value       = yandex_vpc_security_group.k8s_cluster.id
}

output "subnet_security_group_id" {
  description = "ID security group для подсети"
  value       = yandex_vpc_security_group.subnet.id
}
