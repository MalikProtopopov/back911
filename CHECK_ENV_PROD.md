# ⚠️ Проверка .env.prod на сервере

## Проблема: База данных не запускается

Ошибка `container back911-db-1 is unhealthy` означает, что переменные окружения не загружаются из `.env.prod`.

## Решение на сервере:

### 1. Проверить наличие .env.prod

```bash
cd ~/back911
ls -la .env.prod
```

### 2. Если файл не существует, создать его:

```bash
cat > .env.prod << 'EOF'
SECRET_KEY=ЗАМЕНИТЕ_НА_СГЕНЕРИРОВАННЫЙ_КЛЮЧ
DEBUG=False
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=ВАШ_СИЛЬНЫЙ_ПАРОЛЬ_ЗДЕСЬ
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=45.144.221.92,api.911.ru,www.911.ru,911.ru
CORS_ALLOWED_ORIGINS=https://911.ru,https://www.911.ru,http://45.144.221.92
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=60
LOG_LEVEL=INFO
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
EOF

# Отредактировать файл
nano .env.prod
```

### 3. Проверить содержимое .env.prod

```bash
cat .env.prod
```

**Убедитесь, что:**
- `DB_NAME=website_911_db` (не пустое!)
- `DB_USER=postgres` (не пустое!)
- `DB_PASSWORD=ваш_пароль` (не пустое!)

### 4. Генерация SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируйте результат и вставьте в `.env.prod` вместо `SECRET_KEY=...`

### 5. После создания .env.prod, перезапустить:

```bash
# Определить команду docker compose
if docker compose version &> /dev/null; then
    DOCKER_CMD="docker compose"
else
    DOCKER_CMD="docker-compose"
fi

# Остановить все
$DOCKER_CMD -f docker-compose.prod.yml down

# Запустить заново
$DOCKER_CMD -f docker-compose.prod.yml up -d

# Проверить статус
$DOCKER_CMD -f docker-compose.prod.yml ps

# Проверить логи БД
$DOCKER_CMD -f docker-compose.prod.yml logs db
```

## Быстрая проверка переменных:

```bash
# Проверить, что переменные загружаются
cd ~/back911
source .env.prod 2>/dev/null || true
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=${DB_PASSWORD:0:5}..." # Показать только первые 5 символов
```

---

**Важно:** Файл `.env.prod` должен быть в той же директории, что и `docker-compose.prod.yml`!

