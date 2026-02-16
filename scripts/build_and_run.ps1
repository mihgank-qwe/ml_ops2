# Сборка и запуск API в Docker
# Сначала нужно запустить make_dataset и train для создания модели

$ErrorActionPreference = "Stop"

Write-Host "Сборка образа..."
docker build -t credit-api .

Write-Host "Запуск контейнера..."
docker run -p 8000:8000 credit-api
