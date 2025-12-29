# Чеклист переменных окружения для Production

## ✅ Все настройки вынесены в .env.prod

### Обязательные переменные (без них проект не запустится):

```env
# Django
SECRET_KEY=your-very-secret-key-here-min-50-characters

# Database (ОБЯЗАТЕЛЬНО - без дефолтных значений в production!)
DB_NAME=website_911_db
DB_USER=your_db_user
DB_PASSWORD=your_strong_db_password
DB_HOST=db
DB_PORT=5432

# Allowed Hosts (ОБЯЗАТЕЛЬНО!)
ALLOWED_HOSTS=your-domain.com,www.your-domain.com 

# CORS (ОБЯЗАТЕЛЬНО!)
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### Опциональные переменные (есть дефолтные значения):

```env
# Email (опционально)
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
SECURE_SSL_REDIRECT=False
```

## 📋 Что было исправлено:

### 1. **website_project/settings/prod.py**
- ✅ Теперь загружает `.env.prod` вместо `.env`
- ✅ Все настройки берутся из переменных окружения
- ✅ Логирование настраивается через env переменные
- ✅ Email настройки полностью из env

### 2. **website_project/settings/base.py**
- ✅ Дефолтные значения для БД остались только для dev окружения
- ✅ В production все значения должны быть в `.env.prod`

### 3. **Dockerfile**
- ✅ Gunicorn workers и timeout настраиваются через env переменные
- ✅ Можно переопределить через `GUNICORN_WORKERS` и `GUNICORN_TIMEOUT`

### 4. **docker-compose.prod.yml**
- ✅ Добавлены переменные для Gunicorn
- ✅ Все настройки берутся из `.env.prod`

## ⚠️ Важные замечания:

1. **В production НЕТ хардкод значений** - все настройки в `.env.prod`
2. **Дефолтные значения** используются только в dev окружении
3. **Обязательные переменные** должны быть заполнены, иначе проект не запустится
4. **Никогда не коммитьте `.env.prod`** в git (уже в .gitignore)

## 🔍 Проверка перед деплоем:

- [ ] Создан файл `.env.prod`
- [ ] Заполнены все обязательные переменные
- [ ] `SECRET_KEY` сгенерирован и уникален
- [ ] `DB_*` переменные настроены правильно
- [ ] `ALLOWED_HOSTS` содержит все домены
- [ ] `CORS_ALLOWED_ORIGINS` содержит все фронтенд URL
- [ ] Опциональные переменные настроены (если нужны)
- [ ] `.env.prod` не в git (проверено через `git status`)

## 📝 Пример полного .env.prod:

```env
# Django
SECRET_KEY=django-insecure-very-long-and-secure-secret-key-min-50-chars-change-this

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=your_strong_password_here
DB_HOST=db
DB_PORT=5432

# Allowed Hosts
ALLOWED_HOSTS=api.yourdomain.com,www.yourdomain.com,yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password

# Gunicorn (опционально)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60

# Logging (опционально)
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10

# SSL (только после настройки HTTPS!)
# SECURE_SSL_REDIRECT=True
```

---

**Дата:** 2025-01-XX  
**Статус:** ✅ Все настройки вынесены в .env.prod

