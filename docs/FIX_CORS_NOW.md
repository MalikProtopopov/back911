# 🔧 Быстрое исправление CORS для фронтенда

## Проблема
Фронтенд на `http://89.169.1.53/` получает CORS ошибки при запросах к бекенду.

## Решение (выполнить на сервере)

### 1. Откройте файл `.env.prod`

```bash
cd ~/back911
nano .env.prod
```

### 2. Обновите две строки:

**Найдите строку `ALLOWED_HOSTS` и убедитесь, что там есть `89.169.1.53`:**
```env
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53
```

**Найдите строку `CORS_ALLOWED_ORIGINS` и добавьте `http://89.169.1.53` (БЕЗ порта, так как это стандартный порт 80):**
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

⚠️ **ВАЖНО:** 
- БЕЗ пробелов после запятых
- БЕЗ порта `:80` (стандартный HTTP порт не указывается)
- С протоколом `http://`

### 3. Сохраните файл

В nano: `Ctrl+O` (сохранить), `Enter` (подтвердить), `Ctrl+X` (выйти)

### 4. Пересоздайте контейнер web (ВАЖНО: не просто restart!)

```bash
# Пересоздать контейнер с новыми переменными
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d --force-recreate web
```

### 5. Проверьте, что настройки применились

```bash
# Проверить ALLOWED_HOSTS
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"

# Проверить CORS_ALLOWED_ORIGINS
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS)"
```

**Ожидаемый результат:**
```
ALLOWED_HOSTS: ['45.144.221.92', 'api.911.ru', 'www.911.ru', '911.ru', '89.169.1.53']
CORS_ALLOWED_ORIGINS: ['http://45.144.221.92', 'http://89.169.1.53']
```

### 6. Проверьте логи (если нужно)

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs web | tail -20
```

### 7. Обновите страницу фронтенда

Откройте `http://89.169.1.53/` в браузере и проверьте, что CORS ошибки исчезли.

---

## Если не помогло

1. **Проверьте, что URL точно совпадает:**
   - В браузере: `http://89.169.1.53/` (без порта)
   - В `.env.prod`: `http://89.169.1.53` (без порта)

2. **Проверьте, что контейнер пересоздан:**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml ps
   ```
   Посмотрите на время создания контейнера - оно должно быть свежим.

3. **Полный перезапуск (если нужно):**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
   ```

4. **Проверьте, что фронтенд делает запросы к правильному URL:**
   - ✅ **ПРАВИЛЬНО:** `http://45.144.221.92/api/website/...` (бекенд на другом сервере)
   - ❌ **НЕПРАВИЛЬНО:** `http://89.169.1.53/api/website/...` (это адрес фронтенда, не бекенда!)
   
   **Важно:** Фронтенд на `89.169.1.53` должен делать запросы к бекенду на `45.144.221.92`.
   Проверьте в коде фронтенда, что базовый URL API указан как `http://45.144.221.92/api/website/`

---

## Пример правильного `.env.prod`

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

