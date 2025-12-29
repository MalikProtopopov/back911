# 🔍 Диагностика и исправление CORS ошибок

## Проблема
Фронтенд на `http://89.169.1.53/` получает CORS ошибки при запросах к `http://45.144.221.92/api/website/metrics/`

## Шаг 1: Проверьте текущие настройки CORS на бекенде

Выполните на сервере бекенда (`45.144.221.92`):

```bash
cd ~/back911

# Проверить текущие настройки CORS
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS)"
```

**Ожидаемый результат:**
```
CORS_ALLOWED_ORIGINS: ['http://45.144.221.92', 'http://89.169.1.53']
```

Если там нет `http://89.169.1.53` или список пустой - нужно исправить.

## Шаг 2: Проверьте содержимое .env.prod

```bash
# Посмотреть текущие настройки CORS в .env.prod
grep CORS_ALLOWED_ORIGINS ~/back911/.env.prod
```

**Должно быть:**
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

## Шаг 3: Исправьте .env.prod (если нужно)

```bash
nano ~/back911/.env.prod
```

**Убедитесь, что строка `CORS_ALLOWED_ORIGINS` выглядит так:**
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

**Важно:**
- ✅ БЕЗ пробелов после запятых
- ✅ БЕЗ порта `:80` (стандартный HTTP порт не указывается)
- ✅ С протоколом `http://`
- ✅ Оба URL через запятую

**Также проверьте `ALLOWED_HOSTS`:**
```env
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53
```

Сохраните: `Ctrl+O` → `Enter` → `Ctrl+X`

## Шаг 4: Пересоздайте контейнер (ОБЯЗАТЕЛЬНО!)

**⚠️ ВАЖНО: `restart` не перечитывает переменные окружения!**

```bash
# Пересоздать контейнер с новыми переменными
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d --force-recreate web
```

Подождите 10-15 секунд, пока контейнер перезапустится.

## Шаг 5: Проверьте, что настройки применились

```bash
# Проверить CORS настройки
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS); print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"
```

**Ожидаемый результат:**
```
CORS_ALLOWED_ORIGINS: ['http://45.144.221.92', 'http://89.169.1.53']
ALLOWED_HOSTS: ['45.144.221.92', 'api.911.ru', 'www.911.ru', '911.ru', '89.169.1.53']
```

## Шаг 6: Проверьте CORS заголовки в ответе

Проверьте, что бекенд возвращает правильные CORS заголовки:

```bash
# На сервере бекенда или с любого компьютера
curl -H "Origin: http://89.169.1.53" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://45.144.221.92/api/website/metrics/ \
     -v
```

**Ожидаемые заголовки в ответе:**
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: http://89.169.1.53
< Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
< Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with
< Access-Control-Allow-Credentials: true
```

Если заголовка `Access-Control-Allow-Origin: http://89.169.1.53` нет - CORS не настроен правильно.

## Шаг 7: Проверьте логи контейнера

```bash
# Посмотреть последние логи
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs web | tail -30
```

Ищите ошибки или предупреждения.

## Шаг 8: Проверьте в браузере

1. Откройте `http://89.169.1.53/` в браузере
2. Откройте DevTools (F12) → Network
3. Попробуйте сделать запрос к API
4. Посмотрите на заголовки запроса и ответа

**В запросе должен быть заголовок:**
```
Origin: http://89.169.1.53
```

**В ответе должен быть заголовок:**
```
Access-Control-Allow-Origin: http://89.169.1.53
```

## Частые проблемы и решения

### Проблема 1: CORS настройки не применяются

**Причина:** Контейнер не был пересоздан после изменения `.env.prod`

**Решение:**
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d --force-recreate web
```

### Проблема 2: URL не совпадает точно

**Причина:** В CORS указан `http://89.169.1.53:80`, а запросы идут с `http://89.169.1.53`

**Решение:** Уберите порт из CORS настройки:
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

### Проблема 3: Пробелы в .env.prod

**Причина:** В `.env.prod` есть пробелы после запятых

**Решение:** Уберите все пробелы:
```env
# ❌ Неправильно
CORS_ALLOWED_ORIGINS=http://45.144.221.92, http://89.169.1.53

# ✅ Правильно
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

### Проблема 4: Пустые строки в списке

**Причина:** В `.env.prod` есть лишние запятые или пустые значения

**Решение:** Убедитесь, что нет пустых значений:
```env
# ❌ Неправильно
CORS_ALLOWED_ORIGINS=http://45.144.221.92,,http://89.169.1.53

# ✅ Правильно
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

## Полный пример правильного .env.prod

```env
# Django
SECRET_KEY=ваш_секретный_ключ
DEBUG=False

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=db
DB_PORT=5432

# Allowed Hosts
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53

# CORS - фронтенд на стандартном HTTP порту 80
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60
```

## Если ничего не помогло

1. **Полный перезапуск:**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
   ```

2. **Проверьте, что переменные передаются в контейнер:**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web env | grep CORS
   ```

3. **Проверьте, что Django загружает правильный settings файл:**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "import django.conf; print(django.conf.settings.DJANGO_SETTINGS_MODULE)"
   ```
   
   Должно быть: `website_project.settings.prod`

4. **Временно включите DEBUG для диагностики:**
   ```env
   DEBUG=True
   ```
   (Не забудьте вернуть обратно после диагностики!)

