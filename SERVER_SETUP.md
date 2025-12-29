# Инструкция по настройке сервера 45.144.221.92

## 📋 Подготовка сервера

### 1. Подключение к серверу

```bash
ssh root@45.144.221.92
# или
ssh your-user@45.144.221.92
```

### 2. Установка необходимого ПО

```bash
# Обновление системы
apt-get update && apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
apt-get install docker-compose-plugin -y

# Установка Git (если еще не установлен)
apt-get install git -y

# Установка необходимых утилит
apt-get install nano curl wget -y
```

### 3. Настройка Firewall

```bash
# Установка UFW (если не установлен)
apt-get install ufw -y

# Разрешить SSH
ufw allow 22/tcp

# Разрешить HTTP
ufw allow 80/tcp

# Разрешить HTTPS
ufw allow 443/tcp

# Включить firewall
ufw enable

# Проверить статус
ufw status
```

## 🚀 Первоначальный деплой

### 1. Клонирование репозитория

```bash
# Перейти в рабочую директорию
cd /opt
# или
cd /var/www

# Клонировать репозиторий
git clone https://github.com/MalikProtopopov/back911.git
cd back911
```

### 2. Создание .env.prod

```bash
# Скопировать пример
cp .env.prod.example .env.prod

# Отредактировать файл
nano .env.prod
```

**Вставьте содержимое из раздела "Готовый .env.prod" ниже, заменив значения на реальные.**

### 3. Генерация SECRET_KEY

```bash
# Сгенерировать SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируйте сгенерированный ключ и вставьте в `.env.prod` вместо `SECRET_KEY=...`

### 4. Настройка прав доступа

```bash
# Сделать скрипты исполняемыми
chmod +x deploy.sh update.sh

# Убедиться, что .env.prod не доступен для чтения всем
chmod 600 .env.prod
```

### 5. Первый запуск

```bash
# Запустить деплой
./deploy.sh
```

Или вручную:

```bash
# Запуск сервисов
docker-compose -f docker-compose.prod.yml up -d --build

# Применить миграции
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Собрать статику
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Создать суперпользователя
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 🔄 Обновление проекта

### Автоматическое обновление

```bash
cd /opt/back911  # или путь к проекту
./update.sh
```

### Ручное обновление

```bash
cd /opt/back911  # или путь к проекту

# Остановить сервисы
docker-compose -f docker-compose.prod.yml down

# Получить изменения
git pull origin main

# Пересобрать и запустить
docker-compose -f docker-compose.prod.yml up -d --build

# Применить миграции (если есть)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Обновить статику
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Перезапустить
docker-compose -f docker-compose.prod.yml restart web
```

## 📝 Готовый .env.prod для копирования

**⚠️ ВАЖНО:** 
1. Скопируйте содержимое ниже в файл `.env.prod` на сервере
2. Замените значения в угловых скобках `<...>` на реальные!
3. Сгенерируйте SECRET_KEY командой: `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

```env
# ============================================
# Production Environment Variables
# Сервер: 45.144.221.92
# ============================================

# Django
# ⚠️ ОБЯЗАТЕЛЬНО: Сгенерируйте новый SECRET_KEY!
SECRET_KEY=<СГЕНЕРИРУЙТЕ_НОВЫЙ_КЛЮЧ_КОМАНДОЙ_ВЫШЕ>
DEBUG=False

# Database
# ⚠️ ОБЯЗАТЕЛЬНО: Заполните реальными значениями!
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=<ВАШ_СИЛЬНЫЙ_ПАРОЛЬ_БД_МИНИМУМ_16_СИМВОЛОВ>
DB_HOST=db
DB_PORT=5432

# Allowed Hosts
# ⚠️ ОБЯЗАТЕЛЬНО: Укажите все домены и IP адреса
# Через запятую, БЕЗ пробелов
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru

# CORS
# ⚠️ ОБЯЗАТЕЛЬНО: Укажите все URL фронтенда
# Через запятую, БЕЗ пробелов, с протоколом
CORS_ALLOWED_ORIGINS=https://911.ru,https://www.911.ru,http://45.144.221.92

# Email (опционально, для отправки писем)
# Если не нужна отправка писем, можно оставить пустыми
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<ВАШ_EMAIL@gmail.com>
EMAIL_HOST_PASSWORD=<ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ_GMAIL>

# Gunicorn (опционально)
# Количество worker процессов (рекомендуется: количество CPU * 2 + 1)
GUNICORN_WORKERS=4
# Timeout в секундах
GUNICORN_TIMEOUT=60

# Logging (опционально)
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10

# SSL (только после настройки HTTPS!)
# Раскомментируйте и установите True только после настройки SSL сертификатов
# SECURE_SSL_REDIRECT=False
```

### Быстрая команда для создания .env.prod на сервере:

```bash
cat > .env.prod << 'EOF'
# Django
SECRET_KEY=<ВСТАВЬТЕ_СГЕНЕРИРОВАННЫЙ_КЛЮЧ>
DEBUG=False

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=<ВАШ_ПАРОЛЬ>
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
EOF

# Затем отредактируйте файл
nano .env.prod
```

## 🔍 Проверка работы

### Проверка статуса сервисов

```bash
docker-compose -f docker-compose.prod.yml ps
```

Все сервисы должны быть в статусе `Up` и `healthy`.

### Проверка логов

```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Только web
docker-compose -f docker-compose.prod.yml logs -f web

# Только nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Проверка API

```bash
# Проверка доступности API
curl http://45.144.221.92/api/website/metrics/

# Должен вернуть JSON с метриками
```

### Проверка в браузере

- API: http://45.144.221.92/api/website/metrics/
- Swagger: http://45.144.221.92/api/docs/
- Admin: http://45.144.221.92/admin/

## 🛠️ Полезные команды

### Резервное копирование БД

```bash
# Создать бэкап
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres website_911_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из бэкапа
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres website_911_db < backup.sql
```

### Перезапуск сервисов

```bash
# Перезапуск всех
docker-compose -f docker-compose.prod.yml restart

# Перезапуск только web
docker-compose -f docker-compose.prod.yml restart web

# Перезапуск только nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Очистка

```bash
# Остановить и удалить контейнеры
docker-compose -f docker-compose.prod.yml down

# Остановить, удалить контейнеры и volumes (ОСТОРОЖНО - удалит данные!)
docker-compose -f docker-compose.prod.yml down -v

# Очистить неиспользуемые образы
docker system prune -a
```

## 🔒 Безопасность

### Настройка SSH ключей (рекомендуется)

```bash
# На сервере
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Добавить ваш публичный ключ в authorized_keys
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Регулярные обновления

```bash
# Обновление системы
apt-get update && apt-get upgrade -y

# Обновление Docker
apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
```

## 📊 Мониторинг

### Проверка использования ресурсов

```bash
# Использование диска
df -h

# Использование памяти
free -h

# Использование CPU
top

# Docker статистика
docker stats
```

### Логи системы

```bash
# Логи Docker
journalctl -u docker.service -f

# Логи системы
tail -f /var/log/syslog
```

## 🆘 Решение проблем

### Проблема: Сервисы не запускаются

```bash
# Проверить логи
docker-compose -f docker-compose.prod.yml logs

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Пересобрать образы
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Проблема: База данных недоступна

```bash
# Проверить логи БД
docker-compose -f docker-compose.prod.yml logs db

# Проверить подключение
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

### Проблема: Статика не загружается

```bash
# Пересобрать статику
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Проверить права доступа
docker-compose -f docker-compose.prod.yml exec web ls -la /app/static
```

---

**IP сервера:** 45.144.221.92  
**Дата создания:** 2025-01-XX

