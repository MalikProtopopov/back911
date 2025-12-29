# 🔧 Исправление CORS для фронтенда на 89.169.1.53:3000

## Проблема

Фронтенд на `http://89.169.1.53:3000` делает запросы к бэкенду на `http://45.144.221.92`, но получает ошибку CORS:

```
Access to fetch at 'http://45.144.221.92/api/...' from origin 'http://89.169.1.53:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

## Причина

В файле `.env.prod` на сервере не указан правильный `CORS_ALLOWED_ORIGINS` или указан неправильно.

## Решение

### Шаг 1: Подключитесь к серверу

```bash
ssh root@45.144.221.92
cd ~/back911
```

### Шаг 2: Проверьте текущие настройки CORS

```bash
# Проверить, что указано в .env.prod
grep CORS_ALLOWED_ORIGINS .env.prod
```

### Шаг 3: Отредактируйте .env.prod

```bash
nano .env.prod
```

Найдите строку `CORS_ALLOWED_ORIGINS` и убедитесь, что она выглядит так:

```env
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92
```

**⚠️ ВАЖНО:**
- Указывайте **полный URL с протоколом** (http:// или https://)
- Указывайте **точный порт** (если фронт на 3000, то `:3000`)
- Разделяйте запятыми **БЕЗ пробелов**
- **НЕ** добавляйте слэш в конце URL

**Правильно:**
```env
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53
```

**Неправильно:**
```env
CORS_ALLOWED_ORIGINS=89.169.1.53:3000  # ❌ Нет протокола
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000/  # ❌ Есть слэш в конце
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000, http://89.169.1.53  # ❌ Есть пробелы
```

### Шаг 4: Перезапустите контейнеры

```bash
# Перезапустить web контейнер для применения изменений
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml restart web

# Или полностью пересобрать и перезапустить
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
```

### Шаг 5: Проверьте логи

```bash
# Проверить логи web контейнера
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs -f web
```

### Шаг 6: Проверьте CORS с фронтенда

С сервера фронтенда (89.169.1.53) выполните:

```bash
# Проверить, что бэкенд возвращает правильные CORS заголовки
curl -I -H "Origin: http://89.169.1.53:3000" \
     -H "Access-Control-Request-Method: GET" \
     http://45.144.221.92/api/website/services/
```

В ответе должны быть заголовки:
```
Access-Control-Allow-Origin: http://89.169.1.53:3000
Access-Control-Allow-Credentials: true
```

## Быстрая команда (все в одном)

```bash
# На сервере бэкенда (45.144.221.92)
cd ~/back911 && \
nano .env.prod  # Отредактируйте CORS_ALLOWED_ORIGINS
# После сохранения:
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml restart web && \
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs -f web
```

## Пример правильного .env.prod

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# Allowed Hosts (БЕЗ протокола, БЕЗ порта)
ALLOWED_HOSTS=45.144.221.92,89.169.1.53,api.911.ru,www.911.ru,911.ru

# CORS (С протоколом, С портом если не 80/443)
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
```

## Разница между ALLOWED_HOSTS и CORS_ALLOWED_ORIGINS

### ALLOWED_HOSTS
- Указывает, **к каким доменам/IP может обращаться клиент для доступа к бэкенду**
- **БЕЗ** протокола (http/https)
- **БЕЗ** порта
- Пример: `45.144.221.92,api.911.ru`

### CORS_ALLOWED_ORIGINS
- Указывает, **с каких доменов/IP разрешены кросс-доменные запросы к бэкенду**
- **С** протоколом (http:// или https://)
- **С** портом (если не стандартный 80/443)
- Пример: `http://89.169.1.53:3000,https://911.ru`

## Проверка после исправления

### 1. Проверить переменные окружения в контейнере:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web env | grep CORS
```

Должно показать:
```
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92
```

### 2. Проверить в Django shell:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell
```

В shell выполните:
```python
from django.conf import settings
print(settings.CORS_ALLOWED_ORIGINS)
# Должно показать: ['http://89.169.1.53:3000', 'http://89.169.1.53', 'http://45.144.221.92']
```

### 3. Проверить запрос с фронтенда:

Откройте консоль браузера на `http://89.169.1.53:3000` и выполните:

```javascript
fetch('http://45.144.221.92/api/website/services/')
  .then(response => response.json())
  .then(data => console.log('Success:', data))
  .catch(error => console.error('Error:', error));
```

Если всё настроено правильно, запрос должен выполниться без ошибок CORS.

## Дополнительные настройки CORS (опционально)

Если нужны дополнительные настройки CORS, добавьте в `.env.prod`:

```env
# Разрешить отправку cookies и авторизационных заголовков
CORS_ALLOW_CREDENTIALS=true

# Дополнительные заголовки (если нужно)
CORS_ALLOW_HEADERS=content-type,authorization,x-requested-with

# Методы (если нужно ограничить)
CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
```

Затем обновите `website_project/settings/prod.py`:

```python
# CORS settings for production
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Дополнительные настройки (опционально)
if os.getenv("CORS_ALLOW_HEADERS"):
    CORS_ALLOW_HEADERS = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "").split(",") if h.strip()]

if os.getenv("CORS_ALLOW_METHODS"):
    CORS_ALLOW_METHODS = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "").split(",") if m.strip()]
```

## Решение проблем

### Проблема: CORS всё ещё не работает после изменений

**Решение:**
1. Убедитесь, что контейнер перезапущен
2. Проверьте логи: `docker compose logs -f web`
3. Очистите кэш браузера
4. Проверьте, что в `.env.prod` нет лишних пробелов

### Проблема: "CORS_ALLOWED_ORIGINS is empty"

**Решение:**
Проверьте, что в `.env.prod` строка `CORS_ALLOWED_ORIGINS` не закомментирована и не пустая.

### Проблема: Работает с одного домена, но не работает с другого

**Решение:**
Убедитесь, что все нужные домены указаны в `CORS_ALLOWED_ORIGINS` через запятую.

---

**Дата создания:** 2025-01-XX  
**Версия:** 1.0

