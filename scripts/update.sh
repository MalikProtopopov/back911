#!/bin/bash

# Скрипт для обновления проекта на production сервере
# Использование: ./scripts/update.sh или из корня проекта: bash scripts/update.sh

set -e  # Остановка при ошибке

# Переход в корневую директорию проекта (откуда запущен скрипт)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

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
$DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml down

# Очистка старых контейнеров (если есть)
echo "🧹 Очистка старых контейнеров..."
docker ps --filter "name=back911" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true
docker ps -a --filter "name=back911" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true

# Получение последних изменений из git
if [ -d .git ]; then
    echo "📥 Получение последних изменений из git..."
    git pull origin main
else
    echo "⚠️  Git репозиторий не найден, пропускаем git pull"
fi

# Пересборка образов
echo "🔨 Пересборка Docker образов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml build

# Запуск сервисов
echo "▶️  Запуск сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 15

# Применение миграций (если AUTO_MIGRATE не включен в .env.prod)
# Если AUTO_MIGRATE=true, миграции применятся автоматически при перезапуске
if ! grep -q "AUTO_MIGRATE=true" .env.prod 2>/dev/null; then
    echo "🗄️  Проверка и применение миграций..."
    $DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml exec -T web python manage.py migrate --no-input
else
    echo "ℹ️  Миграции будут применены автоматически при перезапуске (AUTO_MIGRATE=true)"
fi

# Статика собирается автоматически при запуске контейнера через entrypoint.sh
echo "ℹ️  Статические файлы собираются автоматически при перезапуске"

# Перезапуск web сервиса для применения изменений
# При перезапуске entrypoint.sh автоматически соберет статику
echo "🔄 Перезапуск web сервиса..."
$DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml restart web

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker/docker-compose.prod.yml ps

echo ""
echo "✅ Обновление завершено!"
echo ""

