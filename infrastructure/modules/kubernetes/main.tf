resource "yandex_iam_service_account" "cluster" {
  name        = "k8s-cluster-${var.environment}"
  description = "Service account for Kubernetes cluster"
  folder_id   = var.folder_id
}

resource "yandex_iam_service_account" "nodes" {
  name        = "k8s-nodes-${var.environment}"
  description = "Service account for Kubernetes nodes"
  folder_id   = var.folder_id
}

resource "yandex_resourcemanager_folder_iam_member" "cluster_roles" {
  folder_id = var.folder_id
  role      = "k8s.clusters.agent"
  member    = "serviceAccount:${yandex_iam_service_account.cluster.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "cluster_vpc" {
  folder_id = var.folder_id
  role      = "vpc.publicAdmin"
  member    = "serviceAccount:${yandex_iam_service_account.cluster.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "cluster_lb" {
  folder_id = var.folder_id
  role      = "load-balancer.admin"
  member    = "serviceAccount:${yandex_iam_service_account.cluster.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "cluster_registry" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.cluster.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "nodes_registry" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.nodes.id}"
}

resource "yandex_kms_symmetric_key" "kms_key" {
  name              = "k8s-${var.environment}-key"
  description       = "KMS key for Kubernetes secrets"
  folder_id         = var.folder_id
  default_algorithm = "AES_128"
  rotation_period   = "8760h"
}

resource "yandex_kubernetes_cluster" "credit_scoring" {
  name        = "credit-scoring-${var.environment}"
  network_id   = var.network_id
  description = "Kubernetes cluster for credit scoring API"

  master {
    version  = "1.28"
    public_ip = true
    zonal {
      zone                = var.zone
      subnet_id           = var.subnet_id
      security_group_ids  = var.master_security_groups
    }
  }

  service_account_id      = yandex_iam_service_account.cluster.id
  node_service_account_id = yandex_iam_service_account.nodes.id

  kms_provider {
    key_id = yandex_kms_symmetric_key.kms_key.id
  }

  release_channel = "STABLE"
}

resource "yandex_kubernetes_node_group" "cpu_nodes" {
  cluster_id  = yandex_kubernetes_cluster.credit_scoring.id
  name        = "cpu-nodes-${var.environment}"
  description = "CPU node group (4 vCPU, 8 GB)"

  instance_template {
    platform_id = "standard-v3"
    resources {
      memory = 8
      cores  = 4
    }
    boot_disk {
      type = "network-ssd"
      size = 64
    }
    scheduling_policy {
      preemptible = var.environment != "production"
    }
  }

  scale_policy {
    auto_scale {
      min     = 2
      max     = 10
      initial = 2
    }
  }

  allocation_policy {
    location {
      zone = var.zone
    }
  }
}

# GPU node group (опционально). Требует предварительно созданный GPU cluster в Yandex Cloud.
# Включить: enable_gpu_nodes = true, указать gpu_cluster_id.
resource "yandex_kubernetes_node_group" "gpu_nodes" {
  count = var.enable_gpu_nodes && var.gpu_cluster_id != "" ? 1 : 0

  cluster_id  = yandex_kubernetes_cluster.credit_scoring.id
  name        = "gpu-nodes-${var.environment}"
  description = "GPU node group для ML inference"

  instance_template {
    platform_id = "gpu-standard-v3"
    resources {
      memory = 32
      cores  = 8
      gpu {
        gpu_cluster_id = var.gpu_cluster_id
      }
    }
    boot_disk {
      type = "network-ssd"
      size = 64
    }
    scheduling_policy {
      preemptible = var.environment != "production"
    }
  }

  scale_policy {
    auto_scale {
      min     = 0
      max     = 2
      initial = 0
    }
  }

  allocation_policy {
    location {
      zone = var.zone
    }
  }
}
