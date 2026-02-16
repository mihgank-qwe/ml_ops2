resource "yandex_vpc_network" "main" {
  name = "credit-scoring-${var.environment}"
}

resource "yandex_vpc_subnet" "main" {
  name           = "subnet-${var.environment}"
  network_id     = yandex_vpc_network.main.id
  zone           = var.zone
  v4_cidr_blocks = ["10.0.1.0/24"]
}
