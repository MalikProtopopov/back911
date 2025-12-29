# Настройка CORS для фронтенда

## Обзор

Для того чтобы фронтенд на `89.169.1.53` мог отправлять запросы к бекенду, нужно обновить два параметра в `.env.prod`:

1. **`ALLOWED_HOSTS`** - разрешает Django принимать запросы с указанных хостов
2. **`CORS_ALLOWED_ORIGINS`** - разрешает браузеру делать CORS запросы с указанных источников

## Что нужно обновить

### 1. Обновите файл `.env.prod` на сервере

Откройте файл `.env.prod` и обновите следующие строки:

```bash
# ALLOWED_HOSTS - добавьте IP фронтенда (если фронт делает запросы напрямую по IP)
# Если фронт обращается к бекенду через домен, IP не нужен
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53

# CORS_ALLOWED_ORIGINS - добавьте полный URL фронтенда с портом
# ⚠️ ВАЖНО: Укажите точный URL с протоколом (http:// или https://) и портом
# Примеры для разных портов:
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53:3000,http://89.169.1.53:80,http://89.169.1.53:8080
```

### 2. Варианты в зависимости от порта фронтенда

#### Если фронт на порту 80 (стандартный HTTP):
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53
```

#### Если фронт на порту 443 (HTTPS):
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,https://89.169.1.53
```

#### Если фронт на порту 3000 (обычно для React/Next.js в dev):
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53:3000
```

#### Если фронт на порту 8080:
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53:8080
```

#### Если фронт на нескольких портах (dev + prod):
```env
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53,http://89.169.1.53:3000,http://89.169.1.53:8080
```

### 3. Если фронт использует домен вместо IP

Если фронтенд доступен по домену (например, `frontend.911.ru`), добавьте домен:

```env
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53,frontend.911.ru
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53,https://frontend.911.ru
```

## После обновления

### 1. ⚠️ ВАЖНО: Пересоздайте контейнер web (не просто restart!)

**`restart` не перечитывает переменные окружения!** Нужно пересоздать контейнер:

```bash
cd ~/back911

# Вариант 1: Пересоздать только web контейнер (рекомендуется)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d --force-recreate web

# Вариант 2: Полный перезапуск (если первый вариант не помог)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
```

**Почему не `restart`?** 
- `restart` только перезапускает существующий контейнер
- Переменные окружения подставляются при **создании** контейнера
- Поэтому нужно `--force-recreate` или `down/up`

### 2. Проверьте настройки:

```bash
# Проверить ALLOWED_HOSTS
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"

# Проверить CORS_ALLOWED_ORIGINS
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS)"
```

## Как узнать порт фронтенда?

Если вы не знаете на каком порту работает фронтенд, проверьте:

1. **Посмотрите конфигурацию фронтенда** (nginx, docker-compose, package.json scripts)
2. **Проверьте открытые порты на сервере:**
   ```bash
   # На сервере с фронтендом
   netstat -tulpn | grep LISTEN
   # или
   ss -tulpn | grep LISTEN
   ```
3. **Проверьте в браузере** - откройте DevTools (F12) → Network → посмотрите на какой URL идут запросы

## Важные замечания

⚠️ **Без пробелов**: В `.env.prod` значения должны быть через запятую БЕЗ пробелов:
- ✅ Правильно: `http://89.169.1.53:3000,http://89.169.1.53:8080`
- ❌ Неправильно: `http://89.169.1.53:3000, http://89.169.1.53:8080`

⚠️ **Протокол обязателен**: Всегда указывайте `http://` или `https://` в `CORS_ALLOWED_ORIGINS`

⚠️ **Порт обязателен**: Если фронт не на стандартном порту (80 для HTTP, 443 для HTTPS), обязательно укажите порт

## Пример полного `.env.prod` с фронтендом

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

# Allowed Hosts - добавлен IP фронтенда
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru,89.169.1.53

# CORS - добавлен URL фронтенда (замените :3000 на ваш порт)
CORS_ALLOWED_ORIGINS=http://45.144.221.92,http://89.169.1.53:3000

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60
```

## Отладка проблем с CORS

Если после настройки фронтенд всё равно получает CORS ошибки:

1. **Проверьте логи бекенда:**
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs web | grep -i cors
   ```

2. **Проверьте заголовки ответа:**
   ```bash
   curl -H "Origin: http://89.169.1.53:3000" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        http://45.144.221.92/api/website/ \
        -v
   ```

3. **Убедитесь что URL точно совпадает** (включая протокол, порт, слеш в конце)

