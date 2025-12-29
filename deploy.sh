#!/bin/bash

# Скрипт для деплоя/обновления проекта на production сервере
# Использование: ./deploy.sh

set -e  # Остановка при ошибке

echo "🚀 Начало деплоя проекта 911 Backend..."

# Проверка наличия .env.prod
if [ ! -f .env.prod ]; then
    echo "❌ ОШИБКА: Файл .env.prod не найден!"
    echo "Создайте файл .env.prod на основе ENV_VARIABLES_CHECKLIST.md"
    exit 1
fi

# Определение команды docker compose (поддержка старого и нового формата)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ ОШИБКА: Docker Compose не найден!"
    exit 1
fi

# Остановка текущих контейнеров
echo "📦 Остановка текущих контейнеров..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml down

# Получение последних изменений из git (если используется)
if [ -d .git ]; then
    echo "📥 Получение последних изменений из git..."
    git pull origin main || echo "⚠️  Git pull не выполнен (не критично)"
fi

# Пересборка образов
echo "🔨 Пересборка Docker образов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml build --no-cache

# Запуск сервисов
echo "▶️  Запуск сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml up -d

# Ожидание готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
sleep 10

# Применение миграций (если AUTO_MIGRATE не включен в .env.prod)
# Если AUTO_MIGRATE=true, миграции применятся автоматически при запуске контейнера
if ! grep -q "AUTO_MIGRATE=true" .env.prod 2>/dev/null; then
    echo "🗄️  Применение миграций базы данных..."
    $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml exec -T web python manage.py migrate --no-input
else
    echo "ℹ️  Миграции будут применены автоматически при запуске (AUTO_MIGRATE=true)"
fi

# Статика теперь собирается автоматически при запуске контейнера через entrypoint.sh
echo "ℹ️  Статические файлы собираются автоматически при запуске контейнера"

# Проверка статуса сервисов
echo "✅ Проверка статуса сервисов..."
$DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml ps

echo ""
echo "🎉 Деплой завершен!"
echo ""
echo "📊 Полезные команды:"
echo "  - Просмотр логов: $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml logs -f"
echo "  - Статус сервисов: $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml ps"
echo "  - Перезапуск: $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml restart"
echo "  - Остановка: $DOCKER_COMPOSE --env-file .env.prod -f docker-compose.prod.yml down"
echo ""

