#!/bin/bash

# =============================================================================
# update_prod.sh - Обновление production сервера с git и перезапуск Docker
# =============================================================================
# Обновляет код с git и перезапускает Docker контейнеры на production сервере
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

echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   ОБНОВЛЕНИЕ PRODUCTION СЕРВЕРА${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""
echo -e "${YELLOW}Сервер: ${PROD_USER}@${PROD_SERVER}${NC}"
echo -e "${YELLOW}Путь: ${PROD_PROJECT_PATH}${NC}"
echo ""

# SSH команда для обновления
ssh "${PROD_USER}@${PROD_SERVER}" << 'ENDSSH'
set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_PATH="/root/back911"
DOCKER_COMPOSE_FILE="$PROJECT_PATH/docker/docker-compose.prod.yml"

cd "$PROJECT_PATH"

echo -e "${YELLOW}Шаг 1/3: Обновление кода с git...${NC}"
git pull
echo -e "${GREEN}✓ Код обновлен${NC}"

echo ""
echo -e "${YELLOW}Шаг 2/3: Пересборка Docker контейнера web...${NC}"
cd docker
docker compose -f docker-compose.prod.yml build web
echo -e "${GREEN}✓ Контейнер пересобран${NC}"

echo ""
echo -e "${YELLOW}Шаг 3/3: Перезапуск Docker контейнеров...${NC}"
docker compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✓ Контейнеры перезапущены${NC}"

echo ""
echo -e "${YELLOW}Проверка статуса контейнеров...${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!${NC}"
echo -e "${GREEN}==============================================================================${NC}"

ENDSSH

echo ""
echo -e "${GREEN}Готово! Проверьте работу сайта:${NC}"
echo "  - API: http://${PROD_SERVER}/api/website/metrics/"
echo "  - Admin: http://${PROD_SERVER}/admin/"

