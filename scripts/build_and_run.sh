#!/bin/bash
# Сборка и запуск API в Docker
# Сначала нужно запустить make_dataset и train для создания модели

set -e

echo "Сборка образа..."
docker build -t credit-api .

echo "Запуск контейнера..."
docker run -p 8000:8000 credit-api
