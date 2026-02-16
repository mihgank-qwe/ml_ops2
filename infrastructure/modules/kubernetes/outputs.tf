output "cluster_id" {
  description = "ID кластера Kubernetes"
  value       = yandex_kubernetes_cluster.credit_scoring.id
}

output "cpu_node_group_id" {
  description = "ID CPU node group"
  value       = yandex_kubernetes_node_group.cpu_nodes.id
}

output "gpu_node_group_id" {
  description = "ID GPU node group (если включена)"
  value       = try(yandex_kubernetes_node_group.gpu_nodes[0].id, null)
}
