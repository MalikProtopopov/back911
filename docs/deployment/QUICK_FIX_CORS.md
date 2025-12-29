# ⚡ Быстрое исправление CORS

## Проблема
Фронтенд `http://89.169.1.53:3000` не может обращаться к бэкенду `http://45.144.221.92`

## Решение (на сервере бэкенда)

### Шаг 1: Подключение
```bash
ssh root@45.144.221.92
cd ~/back911
```

### Шаг 2: Проверка текущих настроек
```bash
grep CORS_ALLOWED_ORIGINS .env.prod
```

### Шаг 3: Редактирование .env.prod
```bash
nano .env.prod
```

Найдите строку `CORS_ALLOWED_ORIGINS` и измените на:
```env
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92
```

**Важно:**
- С протоколом `http://`
- С портом `:3000`
- БЕЗ пробелов после запятых
- БЕЗ слэша в конце

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 4: Перезапуск
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml restart web
```

### Шаг 5: Проверка логов
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs -f web
```

---

## Все команды одной строкой

```bash
cd ~/back911 && \
echo "Текущие настройки CORS:" && \
grep CORS_ALLOWED_ORIGINS .env.prod && \
echo "" && \
echo "Отредактируйте .env.prod и установите:" && \
echo "CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92"
```

После редактирования:
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml restart web && \
sleep 5 && \
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs --tail=50 web
```

---

## Проверка с фронтенда

На сервере фронтенда (89.169.1.53):
```bash
curl -I -H "Origin: http://89.169.1.53:3000" http://45.144.221.92/api/website/services/
```

Должен вернуть:
```
Access-Control-Allow-Origin: http://89.169.1.53:3000
```

---

## Пример правильного .env.prod

```env
SECRET_KEY=your-secret-key
DEBUG=False

DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# БЕЗ протокола, БЕЗ порта
ALLOWED_HOSTS=45.144.221.92,89.169.1.53,api.911.ru

# С протоколом, С портом
CORS_ALLOWED_ORIGINS=http://89.169.1.53:3000,http://89.169.1.53,http://45.144.221.92

GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60
LOG_LEVEL=INFO
```

---

## Если не помогло

1. Проверьте переменные в контейнере:
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web env | grep CORS
```

2. Полный перезапуск:
```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
```

3. Очистите кэш браузера на фронтенде

