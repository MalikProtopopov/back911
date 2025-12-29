#!/bin/bash
set -e

echo "🚀 Starting Django application..."

# Ожидание готовности базы данных (опционально, если нужно)
# Можно использовать wait-for-it или подобный инструмент
# Но так как у нас есть depends_on с healthcheck, это не обязательно

# Применение миграций (если переменная окружения AUTO_MIGRATE=true)
if [ "${AUTO_MIGRATE:-false}" = "true" ]; then
    echo "📦 Applying database migrations..."
    python manage.py migrate --no-input
fi

# Сбор статических файлов
echo "📦 Collecting static files..."
python manage.py collectstatic --no-input

# Запуск Gunicorn
echo "▶️  Starting Gunicorn..."
exec gunicorn website_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --access-logfile - \
    --error-logfile -

