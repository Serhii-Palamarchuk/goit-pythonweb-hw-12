@echo off
REM Збірка та публікація Docker image для goit-pythonweb-hw-10

SET IMAGE_NAME=serhiipalamarchuk/goit-pythonweb-hw-10
SET VERSION=%1
IF "%VERSION%"=="" SET VERSION=latest

echo 🚀 Починаємо збірку Docker image...

REM Збірка image
echo 📦 Збираємо image: %IMAGE_NAME%:%VERSION%
docker build -t %IMAGE_NAME%:%VERSION% -f Dockerfile.prod .

REM Також створюємо тег latest якщо версія не latest
IF NOT "%VERSION%"=="latest" (
    echo 🏷️  Створюємо тег latest
    docker tag %IMAGE_NAME%:%VERSION% %IMAGE_NAME%:latest
)

echo ✅ Збірка завершена!

REM Пуш до Docker Hub
echo 📤 Публікуємо в Docker Hub...
docker push %IMAGE_NAME%:%VERSION%

IF NOT "%VERSION%"=="latest" (
    docker push %IMAGE_NAME%:latest
)

echo 🎉 Публікація завершена!
echo 📋 Використання:
echo    docker pull %IMAGE_NAME%:%VERSION%
echo    docker-compose up

pause