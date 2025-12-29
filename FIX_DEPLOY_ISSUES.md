# 🔧 Исправление проблем при деплое

## Проблема 1: `docker-compose: command not found`

**Решение:** Используйте `docker compose` (без дефиса) - это новый формат команды.

Скрипты уже обновлены и автоматически определяют правильную команду.

**Проверка на сервере:**
```bash
# Проверить, какая команда доступна
docker compose version
# или
docker-compose version
```

## Проблема 2: `poetry.lock: not found`

**Причина:** Файл `poetry.lock` в `.gitignore`, поэтому не попадает в репозиторий.

**Решение 1 (рекомендуется):** Добавить poetry.lock в репозиторий

```bash
# На локальной машине
git add poetry.lock
git commit -m "Add poetry.lock to repository"
git push origin main
```

**Решение 2:** Dockerfile уже обновлен и работает без poetry.lock (создаст автоматически)

## Проблема 3: Переменные окружения не загружаются

**Причина:** Файл `.env.prod` не создан или не в правильной директории.

**Решение:**
```bash
# На сервере
cd ~/back911
nano .env.prod
# Вставить содержимое из env.prod.template
```

## Быстрое исправление на сервере

```bash
# 1. Обновить код
cd ~/back911
git pull origin main

# 2. Создать .env.prod (если еще не создан)
if [ ! -f .env.prod ]; then
    echo "Создайте .env.prod файл!"
    nano .env.prod
fi

# 3. Использовать правильную команду docker compose
# Если docker compose работает:
docker compose -f docker-compose.prod.yml up -d --build

# Если только docker-compose работает:
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Применить миграции
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

## Проверка после исправления

```bash
# Проверить статус
docker compose -f docker-compose.prod.yml ps

# Проверить логи
docker compose -f docker-compose.prod.yml logs web

# Проверить API
curl http://45.144.221.92/api/website/metrics/
```

