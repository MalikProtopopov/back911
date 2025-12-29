# ⚡ Быстрое исправление на сервере 45.144.221.92

## Выполните эти команды на сервере:

```bash
cd ~/back911

# 1. Обновить код из репозитория
git pull origin main

# 2. Создать .env.prod (если еще не создан)
if [ ! -f .env.prod ]; then
    cat > .env.prod << 'EOF'
SECRET_KEY=ЗАМЕНИТЕ_НА_СГЕНЕРИРОВАННЫЙ_КЛЮЧ
DEBUG=False
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=ВАШ_ПАРОЛЬ
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru
CORS_ALLOWED_ORIGINS=https://911.ru,https://www.911.ru,http://45.144.221.92
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
EOF
    nano .env.prod  # Отредактируйте SECRET_KEY и DB_PASSWORD
fi

# 3. Использовать правильную команду docker compose
# Проверить, какая команда работает:
if docker compose version &> /dev/null; then
    DOCKER_CMD="docker compose"
elif docker-compose version &> /dev/null; then
    DOCKER_CMD="docker-compose"
else
    echo "Ошибка: Docker Compose не найден!"
    exit 1
fi

# 4. Остановить старые контейнеры
$DOCKER_CMD -f docker-compose.prod.yml down

# 5. Пересобрать и запустить
$DOCKER_CMD -f docker-compose.prod.yml build --no-cache
$DOCKER_CMD -f docker-compose.prod.yml up -d

# 6. Подождать запуска БД
sleep 10

# 7. Применить миграции
$DOCKER_CMD -f docker-compose.prod.yml exec web python manage.py migrate

# 8. Собрать статику
$DOCKER_CMD -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# 9. Проверить статус
$DOCKER_CMD -f docker-compose.prod.yml ps
```

## Генерация SECRET_KEY:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Проверка работы:

```bash
curl http://45.144.221.92/api/website/metrics/
```

---

**После обновления кода из git, скрипты deploy.sh и update.sh будут автоматически определять правильную команду docker compose.**

