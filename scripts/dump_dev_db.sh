#!/bin/bash

# =============================================================================
# dump_dev_db.sh - Создание дампа dev базы данных
# =============================================================================
# Делает pg_dump из контейнера db в docker-compose.dev.yml
# Сохраняет в backups/dev_dump_YYYY-MM-DD_HH-MM-SS.sql
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переход в корень проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Настройки базы данных (из docker-compose.dev.yml)
DB_USER="postgres"
DB_NAME="website_911_db"
DOCKER_COMPOSE_FILE="docker/docker-compose.dev.yml"

# Директория для бэкапов
BACKUP_DIR="$PROJECT_ROOT/backups"

# Имя файла с timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
DUMP_FILE="$BACKUP_DIR/dev_dump_${TIMESTAMP}.sql"

echo -e "${GREEN}=== Создание дампа Dev базы данных ===${NC}"
echo ""

# Проверяем, запущен ли Docker контейнер
echo -e "${YELLOW}Проверка Docker контейнера...${NC}"
if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps --status running | grep -q "db"; then
    echo -e "${RED}Ошибка: Контейнер db не запущен!${NC}"
    echo "Запустите: docker compose -f $DOCKER_COMPOSE_FILE up -d"
    exit 1
fi
echo -e "${GREEN}✓ Контейнер db запущен${NC}"

# Создаем директорию для бэкапов
mkdir -p "$BACKUP_DIR"

# Добавляем backups/ в .gitignore если еще не добавлен
if ! grep -q "^backups/$" .gitignore 2>/dev/null; then
    echo "backups/" >> .gitignore
    echo -e "${YELLOW}Добавлен backups/ в .gitignore${NC}"
fi

echo ""
echo -e "${YELLOW}Создание дампа базы данных...${NC}"
echo "База: $DB_NAME"
echo "Файл: $DUMP_FILE"
echo ""

# Делаем дамп
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T db \
    pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists > "$DUMP_FILE"

# Проверяем результат
if [ -f "$DUMP_FILE" ] && [ -s "$DUMP_FILE" ]; then
    FILE_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Дамп успешно создан!${NC}"
    echo ""
    echo "Файл: $DUMP_FILE"
    echo "Размер: $FILE_SIZE"
    echo ""
    
    # Создаем симлинк на последний дамп
    LATEST_LINK="$BACKUP_DIR/latest_dev_dump.sql"
    rm -f "$LATEST_LINK"
    ln -s "$(basename "$DUMP_FILE")" "$LATEST_LINK"
    echo -e "${GREEN}✓ Симлинк на последний дамп: $LATEST_LINK${NC}"
else
    echo -e "${RED}Ошибка: Дамп не создан или пустой!${NC}"
    rm -f "$DUMP_FILE"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Готово! ===${NC}"
echo ""
echo "Следующие шаги:"
echo "  1. Скопируйте дамп на сервер: scp $DUMP_FILE root@45.144.221.92:/tmp/"
echo "  2. Или используйте: ./scripts/restore_prod_db.sh $DUMP_FILE"

