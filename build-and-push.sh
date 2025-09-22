#!/bin/bash

# Збірка та публікація Docker image для goit-pythonweb-hw-10

# Налаштування
IMAGE_NAME="serhiipalamarchuk/goit-pythonweb-hw-10"
VERSION=${1:-"latest"}

echo "🚀 Починаємо збірку Docker image..."

# Збірка image
echo "📦 Збираємо image: ${IMAGE_NAME}:${VERSION}"
docker build -t ${IMAGE_NAME}:${VERSION} -f Dockerfile.prod .

# Також створюємо тег latest якщо версія не latest
if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Створюємо тег latest"
    docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest
fi

echo "✅ Збірка завершена!"

# Пуш до Docker Hub
echo "📤 Публікуємо в Docker Hub..."
docker push ${IMAGE_NAME}:${VERSION}

if [ "$VERSION" != "latest" ]; then
    docker push ${IMAGE_NAME}:latest
fi

echo "🎉 Публікація завершена!"
echo "📋 Використання:"
echo "   docker pull ${IMAGE_NAME}:${VERSION}"
echo "   docker-compose up"