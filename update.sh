#!/bin/bash

# Скрипт для обновления проекта на production сервере
# Использование: ./update.sh

set -e  # Остановка при ошибке

echo "🔄 Обновление проекта 911 Backend..."

# Определение команды docker compose (поддержка старого и нового формата)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ ОШИБКА: Docker Compose не найден!"
    exit 1
fi

# Остановка сервисов
echo "⏸️  Остановка сервисов..."
$DOCKER_COMPOSE -f docker-compose.prod.yml down

# Получение последних изменений из git
if [ -d .git ]; then
    echo "📥 Получение последних изменений из git..."
    git pull origin main
else
    echo "⚠️  Git репозиторий не найден, пропускаем git pull"
fi

# Пересборка образов
echo "🔨 Пересборка Docker образов..."
$DOCKER_COMPOSE -f docker-compose.prod.yml build

# Запуск сервисов
echo "▶️  Запуск сервисов..."
$DOCKER_COMPOSE -f docker-compose.prod.yml up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 15

# Применение миграций (если есть новые)
echo "🗄️  Проверка и применение миграций..."
$DOCKER_COMPOSE -f docker-compose.prod.yml exec -T web python manage.py migrate --no-input

# Сбор статики (если изменилась)
echo "📦 Обновление статических файлов..."
$DOCKER_COMPOSE -f docker-compose.prod.yml exec -T web python manage.py collectstatic --no-input

# Перезапуск web сервиса для применения изменений
echo "🔄 Перезапуск web сервиса..."
$DOCKER_COMPOSE -f docker-compose.prod.yml restart web

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
$DOCKER_COMPOSE -f docker-compose.prod.yml ps

echo ""
echo "✅ Обновление завершено!"
echo ""

