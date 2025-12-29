# Руководство по деплою в Production

## 📋 Подготовка к деплою

### 1. Создание файла `.env.prod`

Создайте файл `.env.prod` в корне проекта со следующими переменными:

```env
# Django
SECRET_KEY=your-very-secret-key-here-min-50-characters
DEBUG=False

# Database (ОБЯЗАТЕЛЬНО - без дефолтных значений!)
DB_NAME=website_911_db
DB_USER=your_db_user
DB_PASSWORD=your_strong_db_password
DB_HOST=db
DB_PORT=5432

# Allowed Hosts (через запятую, без пробелов, ОБЯЗАТЕЛЬНО!)
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,api.your-domain.com

# CORS (через запятую, без пробелов, ОБЯЗАТЕЛЬНО!)
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Email (опционально, для отправки писем)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Gunicorn (опционально, по умолчанию workers=4, timeout=60)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60

# Logging (опционально)
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10

# SSL (только после настройки HTTPS!)
# SECURE_SSL_REDIRECT=True
```

**⚠️ ВАЖНО:**
- `SECRET_KEY` должен быть уникальным и сложным (минимум 50 символов)
- `ALLOWED_HOSTS` должен содержать все домены, с которых будет доступен сайт
- `CORS_ALLOWED_ORIGINS` должен содержать точные URL фронтенда (с протоколом)
- Никогда не коммитьте `.env.prod` в git!

### 2. Генерация SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🚀 Деплой на сервер

### Шаг 1: Подключение к серверу

```bash
ssh user@your-server-ip
```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/MalikProtopopov/back911.git
cd back911
```

### Шаг 3: Создание .env.prod

```bash
nano .env.prod
# Вставьте все необходимые переменные окружения
```

### Шаг 4: Запуск проекта

```bash
# Запуск в фоновом режиме
docker-compose -f docker-compose.prod.yml up -d --build
```

### Шаг 5: Применение миграций

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Шаг 6: Сбор статики

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

### Шаг 7: Создание суперпользователя

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Шаг 8: Загрузка начальных данных (опционально)

```bash
docker-compose -f docker-compose.prod.yml exec web bash scripts/import_all_data.sh
```

## 🔒 Настройка HTTPS (SSL)

### Вариант 1: Использование Let's Encrypt (Certbot)

1. Установите certbot на сервере:
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. Получите сертификат:
```bash
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

3. Обновите `nginx.conf`:
   - Раскомментируйте блок HTTPS сервера
   - Укажите пути к сертификатам: `/etc/letsencrypt/live/your-domain.com/fullchain.pem` и `/etc/letsencrypt/live/your-domain.com/privkey.pem`
   - Добавьте volume для сертификатов в `docker-compose.prod.yml`:
   ```yaml
   nginx:
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf:ro
       - /etc/letsencrypt:/etc/letsencrypt:ro
       - static_volume:/app/static
       - media_volume:/app/media
   ```

4. Включите редирект с HTTP на HTTPS в `nginx.conf` (раскомментируйте `return 301`)

5. Перезапустите nginx:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Вариант 2: Использование готовых сертификатов

1. Поместите сертификаты в папку `ssl/` на сервере
2. Обновите `nginx.conf` с путями к сертификатам
3. Добавьте volume для сертификатов в `docker-compose.prod.yml`

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Логи всех сервисов
docker-compose -f docker-compose.prod.yml logs -f

# Логи только web
docker-compose -f docker-compose.prod.yml logs -f web

# Логи nginx
docker-compose -f docker-compose.prod.yml logs -f nginx

# Логи базы данных
docker-compose -f docker-compose.prod.yml logs -f db
```

### Проверка статуса сервисов

```bash
docker-compose -f docker-compose.prod.yml ps
```

### Проверка здоровья сервисов

```bash
# Проверка web
docker-compose -f docker-compose.prod.yml exec web python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/website/metrics/')"

# Проверка базы данных
docker-compose -f docker-compose.prod.yml exec db pg_isready -U your_db_user
```

## 🔄 Обновление проекта

```bash
# 1. Остановить сервисы
docker-compose -f docker-compose.prod.yml down

# 2. Получить последние изменения
git pull origin main

# 3. Пересобрать образы
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Запустить сервисы
docker-compose -f docker-compose.prod.yml up -d

# 5. Применить миграции (если есть новые)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 6. Собрать статику (если изменилась)
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

## 🛠️ Полезные команды

### Резервное копирование базы данных

```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U your_db_user website_911_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Восстановление базы данных

```bash
docker-compose -f docker-compose.prod.yml exec -T db psql -U your_db_user website_911_db < backup.sql
```

### Выполнение команд Django

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py <command>
```

### Доступ к shell контейнера

```bash
docker-compose -f docker-compose.prod.yml exec web bash
```

## ⚠️ Важные замечания

1. **Безопасность:**
   - Никогда не коммитьте `.env.prod` в git
   - Используйте сильные пароли для базы данных
   - Регулярно обновляйте зависимости
   - Настройте firewall на сервере

2. **Производительность:**
   - Настройте количество workers в gunicorn (по умолчанию 4)
   - Используйте CDN для статики (опционально)
   - Настройте кеширование в nginx

3. **Мониторинг:**
   - Настройте мониторинг логов
   - Настройте алерты при падении сервисов
   - Регулярно проверяйте использование дискового пространства

4. **Резервное копирование:**
   - Настройте автоматическое резервное копирование БД
   - Храните бэкапы в безопасном месте
   - Тестируйте восстановление из бэкапов

## 🔧 Настройка firewall (UFW)

```bash
# Разрешить SSH
sudo ufw allow 22/tcp

# Разрешить HTTP
sudo ufw allow 80/tcp

# Разрешить HTTPS
sudo ufw allow 443/tcp

# Включить firewall
sudo ufw enable

# Проверить статус
sudo ufw status
```

## 📝 Чеклист перед деплоем

- [ ] Создан `.env.prod` с правильными значениями
- [ ] `SECRET_KEY` сгенерирован и уникален
- [ ] `ALLOWED_HOSTS` содержит все домены
- [ ] `CORS_ALLOWED_ORIGINS` настроен правильно
- [ ] База данных настроена и доступна
- [ ] SSL сертификаты настроены (если используется HTTPS)
- [ ] Firewall настроен
- [ ] Резервное копирование настроено
- [ ] Мониторинг настроен
- [ ] Домен настроен и указывает на IP сервера

## 🆘 Решение проблем

### Проблема: 502 Bad Gateway

**Решение:**
1. Проверьте, запущен ли web контейнер: `docker-compose -f docker-compose.prod.yml ps`
2. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs web`
3. Проверьте, доступна ли база данных

### Проблема: Static files не загружаются

**Решение:**
1. Убедитесь, что выполнен `collectstatic`
2. Проверьте права доступа к папке static
3. Проверьте настройки nginx для /static/

### Проблема: Database connection error

**Решение:**
1. Проверьте переменные окружения в `.env.prod`
2. Убедитесь, что база данных запущена
3. Проверьте сеть docker-compose

### Проблема: CORS errors

**Решение:**
1. Проверьте `CORS_ALLOWED_ORIGINS` в `.env.prod`
2. Убедитесь, что URL точно совпадают (с протоколом, без слеша в конце)
3. Перезапустите web контейнер

---

**Дата создания:** 2025-01-XX  
**Версия:** 1.0

