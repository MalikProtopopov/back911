#!/bin/bash

# =============================================================================
# restore_prod_db.sh - Восстановление дампа в prod базу данных
# =============================================================================
# Копирует дамп на сервер и восстанавливает его в prod базу
# Использование: ./restore_prod_db.sh [путь_к_дампу]
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

# Настройки сервера
PROD_SERVER="45.144.221.92"
PROD_USER="${PROD_USER:-root}"
PROD_PROJECT_PATH="/root/back911"

# Определяем файл дампа
if [ -n "$1" ]; then
    DUMP_FILE="$1"
else
    # Используем последний дамп
    DUMP_FILE="$PROJECT_ROOT/backups/latest_dev_dump.sql"
fi

# Проверяем, что файл существует
if [ ! -f "$DUMP_FILE" ]; then
    echo -e "${RED}Ошибка: Файл дампа не найден: $DUMP_FILE${NC}"
    echo ""
    echo "Использование: $0 [путь_к_дампу]"
    echo ""
    echo "Доступные дампы:"
    ls -la "$PROJECT_ROOT/backups/"*.sql 2>/dev/null || echo "  (нет дампов)"
    exit 1
fi

# Получаем реальный путь (если это симлинк)
if [ -L "$DUMP_FILE" ]; then
    REAL_DUMP_FILE="$(dirname "$DUMP_FILE")/$(readlink "$DUMP_FILE")"
else
    REAL_DUMP_FILE="$DUMP_FILE"
fi

FILE_SIZE=$(du -h "$REAL_DUMP_FILE" | cut -f1)

echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   ВОССТАНОВЛЕНИЕ ДАННЫХ В PRODUCTION БАЗУ${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""
echo -e "${YELLOW}Дамп: ${REAL_DUMP_FILE}${NC}"
echo -e "${YELLOW}Размер: ${FILE_SIZE}${NC}"
echo -e "${YELLOW}Сервер: ${PROD_USER}@${PROD_SERVER}${NC}"
echo ""
echo -e "${RED}ВНИМАНИЕ: Убедитесь, что вы очистили prod базу перед восстановлением!${NC}"
echo -e "${YELLOW}Для очистки используйте: ./scripts/clean_prod_db.sh${NC}"
echo ""
echo -n "Продолжить? (y/n): "
read CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${YELLOW}Отменено.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Шаг 1/3: Копирование дампа на сервер...${NC}"

# Копируем дамп на сервер
scp "$REAL_DUMP_FILE" "${PROD_USER}@${PROD_SERVER}:/tmp/restore_dump.sql"

echo -e "${GREEN}✓ Дамп скопирован в /tmp/restore_dump.sql${NC}"

echo ""
echo -e "${YELLOW}Шаг 2/3: Восстановление базы данных...${NC}"

# SSH команда для восстановления
ssh "${PROD_USER}@${PROD_SERVER}" << 'ENDSSH'
set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_PATH="/root/back911"
DOCKER_COMPOSE_FILE="$PROJECT_PATH/docker/docker-compose.prod.yml"
ENV_FILE="$PROJECT_PATH/.env.prod"
DUMP_FILE="/tmp/restore_dump.sql"

cd "$PROJECT_PATH"

# Загружаем переменные окружения
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo -e "${RED}Ошибка: Файл $ENV_FILE не найден!${NC}"
    exit 1
fi

echo -e "${YELLOW}База данных: $DB_NAME${NC}"
echo -e "${YELLOW}Пользователь: $DB_USER${NC}"
echo ""

# Проверяем, запущен ли контейнер
if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps --status running | grep -q "db"; then
    echo -e "${RED}Ошибка: Контейнер db не запущен!${NC}"
    exit 1
fi

# Копируем дамп внутрь контейнера
docker cp "$DUMP_FILE" "$(docker compose -f $DOCKER_COMPOSE_FILE ps -q db)":/tmp/restore_dump.sql

# Восстанавливаем из дампа
echo -e "${YELLOW}Выполнение SQL...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T db \
    psql -U "$DB_USER" -d "$DB_NAME" -f /tmp/restore_dump.sql 2>&1 | tail -20

# Удаляем временный файл
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T db rm -f /tmp/restore_dump.sql
rm -f "$DUMP_FILE"

echo ""
echo -e "${GREEN}✓ База данных успешно восстановлена!${NC}"

ENDSSH

echo ""
echo -e "${YELLOW}Шаг 3/3: Применение миграций Django...${NC}"

# Применяем миграции (на случай если структура изменилась)
ssh "${PROD_USER}@${PROD_SERVER}" << 'ENDSSH'
set -e

PROJECT_PATH="/root/back911"
DOCKER_COMPOSE_FILE="$PROJECT_PATH/docker/docker-compose.prod.yml"

cd "$PROJECT_PATH"

# Применяем миграции
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py migrate --no-input

echo -e "${GREEN}✓ Миграции применены${NC}"

ENDSSH

echo ""
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""
echo "Проверьте работу сайта:"
echo "  - API: http://${PROD_SERVER}/api/website/metrics/"
echo "  - Admin: http://${PROD_SERVER}/admin/"

