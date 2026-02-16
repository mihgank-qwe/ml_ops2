# Скопируйте в backend-config.hcl и заполните из вывода bootstrap.
# terraform init -backend-config=backend-config.hcl

bucket     = "your-bucket-name-state"
key        = "infrastructure/terraform.tfstate"
access_key = "YCAJ..."
secret_key = "YCM..."
