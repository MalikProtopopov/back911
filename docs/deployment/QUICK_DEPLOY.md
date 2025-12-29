# 🚀 Быстрый деплой на сервер 45.144.221.92

## Шаг 1: Подключение к серверу

```bash
ssh root@45.144.221.92
# или
ssh your-user@45.144.221.92
```

## Шаг 2: Установка Docker (если еще не установлен)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install docker-compose-plugin -y
```

## Шаг 3: Клонирование проекта

```bash
cd /opt
git clone https://github.com/MalikProtopopov/back911.git
cd back911
```

## Шаг 4: Создание .env.prod

```bash
# Создать файл
nano .env.prod
```

**Вставьте следующее содержимое (замените значения в `<...>`):**

```env
# Django
SECRET_KEY=<СГЕНЕРИРУЙТЕ_НОВЫЙ_КЛЮЧ>
DEBUG=False

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=<ВАШ_СИЛЬНЫЙ_ПАРОЛЬ>
DB_HOST=db
DB_PORT=5432

# Allowed Hosts
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru

# CORS
CORS_ALLOWED_ORIGINS=https://911.ru,https://www.911.ru,http://45.144.221.92

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
```

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Шаг 5: Запуск проекта

```bash
# Сделать скрипты исполняемыми
chmod +x deploy.sh update.sh

# Запустить деплой
./deploy.sh
```

Или вручную:

```bash
# Запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Миграции
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Статика
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Суперпользователь
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Шаг 6: Проверка

```bash
# Статус
docker-compose -f docker-compose.prod.yml ps

# Проверка API
curl http://45.144.221.92/api/website/metrics/
```

## 🔄 Обновление проекта

```bash
cd /opt/back911
./update.sh
```

---

**Готово!** Проект доступен по адресу: http://45.144.221.92

