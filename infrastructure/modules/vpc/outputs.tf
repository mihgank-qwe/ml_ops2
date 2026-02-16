output "network_id" {
  description = "ID сети VPC"
  value       = yandex_vpc_network.main.id
}

output "subnet_id" {
  description = "ID подсети"
  value       = yandex_vpc_subnet.main.id
}
