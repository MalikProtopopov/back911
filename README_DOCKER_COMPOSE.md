# Упрощение команд Docker Compose

Чтобы использовать короткие команды вместо длинных `docker compose --env-file .env.prod -f docker/docker-compose.prod.yml`, используйте переменную окружения `COMPOSE_FILE`.

## Настройка (один раз)

Добавьте в ваш `~/.bashrc` или `~/.zshrc`:

```bash
# Для production окружения
export COMPOSE_FILE=docker/docker-compose.prod.yml
```

Или создайте файл `.env` в корне проекта (Docker Compose автоматически читает его):

```bash
# .env (в корне проекта)
COMPOSE_FILE=docker/docker-compose.prod.yml
```

## Использование

После настройки можно использовать короткие команды:

```bash
# Вместо: docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
docker compose up -d

# Вместо: docker compose --env-file .env.prod -f docker/docker-compose.prod.yml down
docker compose down

# Вместо: docker compose --env-file .env.prod -f docker/docker-compose.prod.yml ps
docker compose ps

# И так далее...
```

## Важно

- Переменные окружения из `.env.prod` автоматически загружаются через `env_file` в docker-compose.yml
- Команды нужно запускать из корня проекта
- Если нужно переключиться на dev окружение, измените `COMPOSE_FILE` на `docker/docker-compose.dev.yml`

