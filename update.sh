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
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml down

# Получение последних изменений из git
if [ -d .git ]; then
    echo "📥 Получение последних изменений из git..."
    git pull origin main
else
    echo "⚠️  Git репозиторий не найден, пропускаем git pull"
fi

# Пересборка образов
echo "🔨 Пересборка Docker образов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml build

# Запуск сервисов
echo "▶️  Запуск сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 15

# Применение миграций (если AUTO_MIGRATE не включен в .env.prod)
# Если AUTO_MIGRATE=true, миграции применятся автоматически при перезапуске
if ! grep -q "AUTO_MIGRATE=true" .env.prod 2>/dev/null; then
    echo "🗄️  Проверка и применение миграций..."
    $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml exec -T web python manage.py migrate --no-input
else
    echo "ℹ️  Миграции будут применены автоматически при перезапуске (AUTO_MIGRATE=true)"
fi

# Статика собирается автоматически при запуске контейнера через entrypoint.sh
echo "ℹ️  Статические файлы собираются автоматически при перезапуске"

# Перезапуск web сервиса для применения изменений
# При перезапуске entrypoint.sh автоматически соберет статику
echo "🔄 Перезапуск web сервиса..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml restart web

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml ps

echo ""
echo "✅ Обновление завершено!"
echo ""

