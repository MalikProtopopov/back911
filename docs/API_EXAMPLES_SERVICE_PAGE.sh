#!/bin/bash
# API примеры для страницы услуги в городе
# Запуск: bash docs/API_EXAMPLES_SERVICE_PAGE.sh

BASE_URL="http://localhost:8000"

echo "=============================================="
echo "API запросы для страницы услуги в городе"
echo "=============================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ================================================
# 1. ОСНОВНОЙ ЭНДПОИНТ (РЕКОМЕНДУЕТСЯ)
# ================================================

echo -e "${GREEN}1. ОСНОВНОЙ ЭНДПОИНТ - Вся информация одним запросом${NC}"
echo -e "${BLUE}GET /api/website/cities/moskva/services/shinomontazh/${NC}"
echo ""

curl -s "${BASE_URL}/api/website/cities/moskva/services/shinomontazh/" | python3 -m json.tool | head -80

echo ""
echo "---"
echo ""

# ================================================
# 2. ОПЦИИ ПО ГОРОДУ И УСЛУГЕ
# ================================================

echo -e "${GREEN}2. ОПЦИИ С ЦЕНАМИ - По городу и услуге${NC}"
echo -e "${BLUE}GET /api/website/options/by-city/?city=moskva&service=shinomontazh${NC}"
echo ""

curl -s "${BASE_URL}/api/website/options/by-city/?city=moskva&service=shinomontazh" | python3 -m json.tool | head -40

echo ""
echo "---"
echo ""

# ================================================
# 3. ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ОБ ОПЦИИ (ВСЕ ЦЕНЫ)
# ================================================

echo -e "${GREEN}3. ДЕТАЛЬНАЯ ОПЦИЯ - Все цены по всем городам и категориям${NC}"
echo -e "${BLUE}GET /api/website/options/1/${NC}"
echo ""

OPTION_DETAIL=$(curl -s "${BASE_URL}/api/website/options/1/")

echo "$OPTION_DETAIL" | python3 << 'PYTHON'
import sys, json

data = json.load(sys.stdin)

print(f"Опция: {data['title']}")
print(f"Услуга: {data['service_title']}")
print(f"Всего цен: {len(data['prices'])}")
print("\nЦены для Москвы:")

moscow_prices = [p for p in data['prices'] if p['city_slug'] == 'moskva']
for price in moscow_prices[:5]:
    tech_cat = price['technic_category_title'] or 'Без категории'
    print(f"  - {tech_cat}: {price['amount']} руб.")

if len(moscow_prices) > 5:
    print(f"  ... и еще {len(moscow_prices) - 5} цен")
PYTHON

echo ""
echo "---"
echo ""

# ================================================
# 4. СПИСОК КАТЕГОРИЙ ТЕХНИКИ
# ================================================

echo -e "${GREEN}4. КАТЕГОРИИ ТЕХНИКИ - Для фильтрации цен${NC}"
echo -e "${BLUE}GET /api/website/technic-categories/?service__slug=shinomontazh${NC}"
echo ""

curl -s "${BASE_URL}/api/website/technic-categories/?service__slug=shinomontazh" | python3 -m json.tool

echo ""
echo "---"
echo ""

# ================================================
# 5. СРАВНЕНИЕ ДАННЫХ
# ================================================

echo -e "${GREEN}5. АНАЛИЗ - Сколько опций и цен в Москве для шиномонтажа${NC}"
echo ""

# Получаем данные
CITY_SERVICE=$(curl -s "${BASE_URL}/api/website/cities/moskva/services/shinomontazh/")
BY_CITY=$(curl -s "${BASE_URL}/api/website/options/by-city/?city=moskva&service=shinomontazh")

echo "$CITY_SERVICE" | python3 << 'PYTHON'
import sys, json

data = json.load(sys.stdin)

print(f"Город: {data['city']['title']}")
print(f"Услуга: {data['service']['title']}")
print(f"Опций с ценами: {len(data['options'])}")
print(f"\nПервые 3 опции:")

for i, opt in enumerate(data['options'][:3], 1):
    price_info = opt['price']
    if price_info:
        tech = price_info.get('technic_category', 'Не указана')
        print(f"{i}. {opt['title']}")
        print(f"   Цена: {price_info['amount']} руб.")
        print(f"   Категория: {tech}")
    else:
        print(f"{i}. {opt['title']} - нет цены")
PYTHON

echo ""
echo "---"
echo ""

# ================================================
# 6. ПРОВЕРКА НАЛИЧИЯ ВСЕХ ДАННЫХ
# ================================================

echo -e "${GREEN}6. ПРОВЕРКА ПОЛНОТЫ ДАННЫХ${NC}"
echo ""

curl -s "${BASE_URL}/api/website/cities/moskva/services/shinomontazh/" | python3 << 'PYTHON'
import sys, json

data = json.load(sys.stdin)

checks = {
    "✓ Информация о городе": data.get('city') is not None,
    "✓ Информация об услуге": data.get('service') is not None,
    "✓ Список опций": data.get('options') is not None and len(data['options']) > 0,
    "✓ HTML контент": data.get('content') is not None,
    "✓ SEO метаданные": data.get('seo') is not None,
}

for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check}")

print(f"\nОпций в ответе: {len(data.get('options', []))}")

# Проверка структуры цен
options_with_price = [opt for opt in data.get('options', []) if opt.get('price')]
options_without_price = len(data.get('options', [])) - len(options_with_price)

print(f"Опций с ценой: {len(options_with_price)}")
print(f"Опций без цены: {options_without_price}")

# Проверка категорий техники
categories = set()
for opt in data.get('options', []):
    if opt.get('price') and opt['price'].get('technic_category'):
        categories.add(opt['price']['technic_category'])

print(f"\nНайдено категорий техники: {len(categories)}")
for cat in sorted(categories):
    print(f"  - {cat}")
PYTHON

echo ""
echo "=============================================="
echo "Готово!"
echo "=============================================="
