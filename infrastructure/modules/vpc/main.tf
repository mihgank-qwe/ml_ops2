resource "yandex_vpc_network" "main" {
  name = "credit-scoring-${var.environment}"
}

resource "yandex_vpc_subnet" "main" {
  name           = "subnet-${var.environment}"
  network_id     = yandex_vpc_network.main.id
  zone           = var.zone
  v4_cidr_blocks = ["10.0.1.0/24"]
}

# Security group для Kubernetes кластера
resource "yandex_vpc_security_group" "k8s_cluster" {
  name        = "k8s-cluster-${var.environment}"
  description = "Security group for Kubernetes cluster"
  network_id  = yandex_vpc_network.main.id

  # Kubernetes API (kubectl)
  ingress {
    protocol       = "TCP"
    port           = 6443
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Kubernetes API"
  }

  # HTTPS (Ingress)
  ingress {
    protocol       = "TCP"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "HTTPS"
  }

  # HTTP (Ingress)
  ingress {
    protocol       = "TCP"
    port           = 80
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "HTTP"
  }

  # Внутренний трафик между нодами
  ingress {
    protocol       = "ANY"
    v4_cidr_blocks = ["10.0.0.0/8"]
    description    = "Internal cluster traffic"
  }

  # Health checks для Load Balancer
  ingress {
    protocol          = "TCP"
    port              = 30080
    predefined_target = "loadbalancer_healthchecks"
    description       = "LB health checks"
  }

  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Outbound"
  }
}

# Security group для общего доступа к подсети
resource "yandex_vpc_security_group" "subnet" {
  name        = "subnet-${var.environment}"
  description = "Security group for subnet access"
  network_id  = yandex_vpc_network.main.id

  # API приложения (порт 8000)
  ingress {
    protocol       = "TCP"
    port           = 8000
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Credit scoring API"
  }

  ingress {
    protocol       = "TCP"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "HTTPS"
  }

  ingress {
    protocol       = "TCP"
    port           = 80
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "HTTP"
  }

  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Outbound"
  }
}
