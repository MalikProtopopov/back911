#!/bin/bash

# =============================================================================
# clean_prod_db.sh - Очистка prod базы данных
# =============================================================================
# ВНИМАНИЕ: Этот скрипт ПОЛНОСТЬЮ УДАЛЯЕТ все данные из prod базы!
# Запускается на удаленном сервере через SSH
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Настройки сервера
PROD_SERVER="45.144.221.92"
PROD_USER="${PROD_USER:-root}"
PROD_PROJECT_PATH="/root/back911"
DOCKER_COMPOSE_FILE="$PROD_PROJECT_PATH/docker/docker-compose.prod.yml"
ENV_FILE="$PROD_PROJECT_PATH/.env.prod"

echo -e "${RED}==============================================================================${NC}"
echo -e "${RED}   ВНИМАНИЕ! ОЧИСТКА PRODUCTION БАЗЫ ДАННЫХ!${NC}"
echo -e "${RED}==============================================================================${NC}"
echo ""
echo -e "${YELLOW}Сервер: ${PROD_USER}@${PROD_SERVER}${NC}"
echo -e "${YELLOW}Путь: ${PROD_PROJECT_PATH}${NC}"
echo ""
echo -e "${RED}ЭТО ДЕЙСТВИЕ УДАЛИТ ВСЕ ДАННЫЕ ИЗ PRODUCTION БАЗЫ!${NC}"
echo ""
echo -n "Введите 'YES' для подтверждения: "
read CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo -e "${YELLOW}Отменено.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Подключение к серверу...${NC}"

# SSH команда для очистки базы
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

cd "$PROJECT_PATH"

# Загружаем переменные окружения
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo -e "${GREEN}✓ Загружены переменные из .env.prod${NC}"
else
    echo -e "${RED}Ошибка: Файл $ENV_FILE не найден!${NC}"
    exit 1
fi

# Проверяем, что переменные загружены
if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
    echo -e "${RED}Ошибка: DB_USER или DB_NAME не заданы в .env.prod${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}База данных: $DB_NAME${NC}"
echo -e "${YELLOW}Пользователь: $DB_USER${NC}"
echo ""

# Проверяем, запущен ли контейнер
echo -e "${YELLOW}Проверка Docker контейнера...${NC}"
if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps --status running | grep -q "db"; then
    echo -e "${RED}Ошибка: Контейнер db не запущен!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Контейнер db запущен${NC}"

echo ""
echo -e "${YELLOW}Очистка базы данных...${NC}"

# Удаляем схему public и пересоздаем
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T db \
    psql -U "$DB_USER" -d "$DB_NAME" << 'SQLEND'
-- Удаляем все таблицы через DROP SCHEMA
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Восстанавливаем права по умолчанию
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
SQLEND

echo ""
echo -e "${GREEN}✓ База данных $DB_NAME полностью очищена!${NC}"
echo ""
echo "Теперь можно восстановить данные из дампа."

ENDSSH

echo ""
echo -e "${GREEN}=== Очистка завершена! ===${NC}"
echo ""
echo "Следующий шаг:"
echo "  ./scripts/restore_prod_db.sh backups/latest_dev_dump.sql"

