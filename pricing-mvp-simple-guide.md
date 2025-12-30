# Рекомендации для Справочника с Калькулятором Цены
## Упрощённая архитектура для сайта (НЕ для масштабной системы)

---

## 📋 Контекст: Что вы реально делаете

**ВЫ ДЕЛАЕТЕ:** 
- ✅ Справочник с калькулятором цены на сайте
- ✅ Пользователи видят примеры цен
- ✅ (Потенциально) Кнопка "Заказать" для заявки

**ВЫ НЕ ДЕЛАЕТЕ (пока):**
- ❌ Сложную систему управления заказами
- ❌ 1000+ одновременных пользователей
- ❌ A/B тестирование цен
- ❌ Микросервисную архитектуру

---

## ✅ ЧТО РЕАЛЬНО НУЖНО (Top 3)

### 1️⃣ Понятная структура БД (чтобы быстро менять цены)

```sql
-- ВАРИАНТ 1: Простой (рекомендуемый для MVP)
CREATE TABLE cities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    is_active BOOLEAN
);

CREATE TABLE services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150),
    description TEXT,
    base_price DECIMAL(10, 2),
    is_active BOOLEAN
);

CREATE TABLE service_options (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    name VARCHAR(150),
    price_modifier DECIMAL(10, 2),
    is_active BOOLEAN,
    FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parameter_type ENUM('TIRE_SIZE', 'VEHICLE_CATEGORY', 'FUEL_TYPE'),
    value VARCHAR(100),
    price_modifier DECIMAL(10, 2),
    sort_order INT,
    is_active BOOLEAN
);

CREATE TABLE delivery_zones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    zone_name VARCHAR(100),
    delivery_price DECIMAL(10, 2),
    is_active BOOLEAN,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Всё. Остальное вычисляется в приложении.
```

**Преимущества:**
- 5 таблиц вместо 15
- Легко менять цены через админ-панель
- Минимум JOIN'ов в запросах
- Понятная логика

**Как работает расчёт цены:**
```
price = service.base_price 
      + sum(selected_options.price_modifier)
      + sum(selected_parameters.price_modifier)
      + delivery_zone.delivery_price
```

---

### 2️⃣ Простой кэш для быстроты (не Redis, просто в памяти приложения)

```python
# На Python (FastAPI, Django)

import json
from datetime import datetime, timedelta

class PricingCache:
    """
    Простой in-memory кэш для параметров ценообразования.
    Не нужен Redis для справочника!
    """
    
    def __init__(self, ttl_minutes=60):
        self.cache = {}
        self.ttl = ttl_minutes * 60  # в секундах
        self.last_update = {}
    
    def load_pricing_data(self, db):
        """Загружаем всё в память один раз"""
        
        # Города
        self.cache['cities'] = {
            city['id']: city 
            for city in db.query("SELECT * FROM cities WHERE is_active = TRUE")
        }
        
        # Услуги
        self.cache['services'] = {
            service['id']: service 
            for service in db.query("SELECT * FROM services WHERE is_active = TRUE")
        }
        
        # Опции услуг (группируем по service_id)
        self.cache['service_options'] = {}
        for option in db.query("SELECT * FROM service_options WHERE is_active = TRUE"):
            service_id = option['service_id']
            if service_id not in self.cache['service_options']:
                self.cache['service_options'][service_id] = []
            self.cache['service_options'][service_id].append(option)
        
        # Параметры (группируем по типу)
        self.cache['parameters'] = {}
        for param in db.query("SELECT * FROM parameters WHERE is_active = TRUE"):
            param_type = param['parameter_type']
            if param_type not in self.cache['parameters']:
                self.cache['parameters'][param_type] = []
            self.cache['parameters'][param_type].append(param)
        
        # Зоны доставки (группируем по городу)
        self.cache['delivery_zones'] = {}
        for zone in db.query("SELECT * FROM delivery_zones WHERE is_active = TRUE"):
            city_id = zone['city_id']
            if city_id not in self.cache['delivery_zones']:
                self.cache['delivery_zones'][city_id] = []
            self.cache['delivery_zones'][city_id].append(zone)
        
        self.last_update['all'] = datetime.now()
    
    def get_cities(self, db):
        """Вернуть города (с проверкой TTL)"""
        if self._needs_update('all'):
            self.load_pricing_data(db)
        return self.cache.get('cities', {})
    
    def get_service_options(self, service_id, db):
        """Вернуть опции для услуги"""
        if self._needs_update('all'):
            self.load_pricing_data(db)
        return self.cache.get('service_options', {}).get(service_id, [])
    
    def get_parameters_by_type(self, param_type, db):
        """Вернуть параметры по типу"""
        if self._needs_update('all'):
            self.load_pricing_data(db)
        return self.cache.get('parameters', {}).get(param_type, [])
    
    def _needs_update(self, key):
        """Проверить, истёк ли TTL"""
        if key not in self.last_update:
            return True
        elapsed = (datetime.now() - self.last_update[key]).total_seconds()
        return elapsed > self.ttl
    
    def invalidate(self, key='all'):
        """Очистить кэш (вызвать при изменении цены)"""
        if key == 'all':
            self.cache.clear()
            self.last_update.clear()
        else:
            self.cache.pop(key, None)
            self.last_update.pop(key, None)

# Инициализируем один раз при старте приложения
pricing_cache = PricingCache(ttl_minutes=60)

# Используем в FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/pricing/calculate")
def calculate_price(
    service_id: int,
    city_id: int,
    tire_size_id: int = None,
    vehicle_category_id: int = None,
    option_ids: list[int] = None,
    db = Depends(get_db)
):
    """API для расчёта цены"""
    
    # 1. Загружаем данные (из кэша)
    services = pricing_cache.get_cities(db)  # на самом деле нужна функция get_services
    
    # 2. Простой расчёт
    service = services.get(service_id)
    if not service:
        return {"error": "Service not found"}
    
    price = float(service['base_price'])
    
    # Добавляем опции
    if option_ids:
        options = pricing_cache.get_service_options(service_id, db)
        for option in options:
            if option['id'] in option_ids:
                price += float(option['price_modifier'])
    
    # Добавляем параметры
    if tire_size_id:
        tire_params = pricing_cache.get_parameters_by_type('TIRE_SIZE', db)
        for param in tire_params:
            if param['id'] == tire_size_id:
                price += float(param['price_modifier'])
    
    # Добавляем доставку
    delivery_zones = pricing_cache.cache.get('delivery_zones', {}).get(city_id, [])
    delivery_price = 0
    if delivery_zones:
        delivery_price = float(delivery_zones[0]['delivery_price'])
    
    return {
        "service_id": service_id,
        "base_price": float(service['base_price']),
        "total_price": price + delivery_price,
        "breakdown": {
            "service": float(service['base_price']),
            "modifiers": price - float(service['base_price']),
            "delivery": delivery_price
        }
    }
```

**Почему этот подход:**
- ✅ Один запрос в БД при старте (не на каждый запрос)
- ✅ Быстро (всё в памяти)
- ✅ Не нужен Redis
- ✅ Автоматически перезагружается каждый час
- ✅ Можно очистить при изменении цены

---

### 3️⃣ История изменений (простая таблица логов)

```sql
-- ТАБЛИЦА логов (для аудита "когда была изменена цена")
CREATE TABLE price_changes_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    entity_type ENUM('SERVICE', 'OPTION', 'PARAMETER', 'DELIVERY_ZONE'),
    entity_id INT,
    
    old_value DECIMAL(10, 2),
    new_value DECIMAL(10, 2),
    
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),  -- email админа
    reason TEXT,  -- опционально: "Сезонная скидка", "Ошибка", и т.д.
    
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_changed_at (changed_at)
);

-- Пример: когда меняете цену услуги
INSERT INTO price_changes_log (entity_type, entity_id, old_value, new_value, changed_by, reason)
VALUES ('SERVICE', 1, 2000, 2500, 'admin@company.com', 'Q1 2025 price increase');

-- Пример: посмотреть историю
SELECT * FROM price_changes_log 
WHERE entity_type = 'SERVICE' AND entity_id = 1
ORDER BY changed_at DESC;
```

**Это даёт:**
- ✅ Полный аудит кто и когда менял цены
- ✅ Возможность объяснить клиентам: "Цена подросла потому что..."
- ✅ Данные для анализа: как часто меняются цены

---

## ⚙️ КАК ВНЕДРИТЬ (пошагово)

### Фаза 1: БД + API (Неделя 1)

1. Создать 5 таблиц (города, услуги, опции, параметры, зоны)
2. Написать миграции
3. Заполнить тестовые данные
4. Создать API endpoint `/api/pricing/calculate`

### Фаза 2: Frontend калькулятор (Неделя 2)

1. Взять ваш текущий HTML калькулятор
2. Добавить fetch к API вместо жёсткого кода
3. Тестировать

### Фаза 3: Админ-панель (Неделя 3)

1. CRUD для услуг
2. CRUD для параметров
3. CRUD для опций
4. При изменении → логируем в `price_changes_log`

---

## 🚫 ЧТО НЕ НУЖНО (забудьте про это)

| Что | Почему не нужно |
|-----|-----------------|
| **Redis кэш** | Один in-memory кэш в приложении достаточно |
| **Версионирование правил** | Нет динамических правил, всё в БД |
| **Группы правил с приоритетами** | Ваш расчёт простой: база + опции + параметры + доставка |
| **A/B тестирование цен** | Пока справочник, не e-commerce |
| **Multi-tenant архитектура** | Один бизнес = одна схема |
| **Race conditions защита** | Справочник читается > пишется, не критично |
| **Сложные индексы** | 5 таблиц, полный скан быстро |

---

## 💡 НЮАНСЫ (реальные проблемы, которые могут быть)

### Нюанс 1: Асинхронные обновления кэша

**Проблема:**
```
Вы обновили цену в БД.
Но пользователь видит старую цену из кэша (он кэшируется на 60 минут).
```

**Решение:**
```python
# При изменении цены - очищаем кэш ИМ ЖЕ
def update_service_price(service_id, new_price, db):
    # 1. Обновляем БД
    db.update(f"UPDATE services SET base_price = {new_price} WHERE id = {service_id}")
    
    # 2. Очищаем кэш СРАЗУ ЖЕ
    pricing_cache.invalidate('all')  # или точнее: invalidate('services')
    
    # 3. Логируем
    db.insert("INSERT INTO price_changes_log ...", ...)
    
    return {"status": "updated"}
```

---

### Нюанс 2: Разные цены в разных местах сайта

**Проблема:**
```
На странице "Услуги" показана цена 2000 ₽
На странице "Калькулятор" показана цена 2000 ₽ + опции
На странице "Главная" показана цена 2000 ₽

Если меняется базовая цена, нужно обновить три места.
```

**Решение:**
```python
# Используйте ОДНУ функцию для расчёта везде

def get_service_price(service_id, options=None, db=None):
    """Единая функция для расчёта цены"""
    service = pricing_cache.get_service(service_id)
    price = float(service['base_price'])
    
    if options:
        # добавляем опции
        pass
    
    return price

# На странице услуг:
price = get_service_price(1)  # 2000

# На калькуляторе:
price = get_service_price(1, options=[1, 2])  # 2000 + опции

# На главной:
price = get_service_price(1)  # 2000
```

**Вывод:** Один источник истины для расчёта.

---

### Нюанс 3: Валидация цен при изменении

**Проблема:**
```
Админ случайно установил цену 0.01 ₽ вместо 1000 ₽
Нужна защита от таких ошибок.
```

**Решение:**
```python
MIN_PRICE = 100  # минимальная цена 100 ₽
MAX_PRICE = 50000  # максимальная цена 50000 ₽

def validate_price(price):
    if price < MIN_PRICE:
        raise ValueError(f"Цена не может быть ниже {MIN_PRICE}")
    if price > MAX_PRICE:
        raise ValueError(f"Цена не может быть больше {MAX_PRICE}")
    return True

# При сохранении цены:
try:
    validate_price(new_price)
    update_service_price(service_id, new_price, db)
except ValueError as e:
    return {"error": str(e)}
```

---

### Нюанс 4: Запрос "Сколько это будет стоить в разных городах?"

**Проблема:**
```
Пользователь хочет видеть цену в Москве vs Питере.
Нужно быстро показать варианты.
```

**Решение:**
```python
@app.get("/api/pricing/compare-cities")
def compare_cities(service_id: int, db=Depends(get_db)):
    """Вернуть цену во всех городах"""
    
    cities = pricing_cache.cache['cities']
    delivery_zones = pricing_cache.cache['delivery_zones']
    service = pricing_cache.cache['services'][service_id]
    
    result = []
    for city_id, city in cities.items():
        zones = delivery_zones.get(city_id, [])
        
        # Берём первую зону как базовую доставку
        delivery_price = float(zones[0]['delivery_price']) if zones else 0
        
        result.append({
            "city": city['name'],
            "city_id": city_id,
            "base_price": float(service['base_price']),
            "delivery_price": delivery_price,
            "total_price": float(service['base_price']) + delivery_price
        })
    
    return result
```

---

## 📋 ЧЕК-ЛИСТ ДЛЯ ВАШЕГО MVP

- [ ] **БД структура** - 5 основных таблиц созданы
- [ ] **API endpoint** `/api/pricing/calculate` работает
- [ ] **In-memory кэш** реализован с TTL
- [ ] **История изменений** таблица логирует все изменения цен
- [ ] **Валидация цен** - есть мин/макс ограничения
- [ ] **Frontend калькулятор** получает данные с API
- [ ] **Админ-панель** позволяет менять цены
- [ ] **При изменении цены** кэш очищается
- [ ] **Таблица логов** показывает кто и когда менял цены

---

## 🎯 ВЫВОД

**Для справочника с калькулятором:**

✅ **НУЖНО:**
- Простая БД (5 таблиц)
- In-memory кэш (не Redis)
- Таблица логов изменений
- Быстрый API для расчётов
- Админ-панель для управления ценами

❌ **НЕ НУЖНО:**
- Версионирование правил
- Кэширование в Redis
- A/B тестирование
- Сложные приоритеты правил
- Multi-tenant архитектура

**Сложность:** ⭐⭐ (легко)
**Время разработки:** 2-3 недели
**Масштабируемость:** До 10000 пользователей в день без проблем

Когда потом захотите добавить реальные заказы и отследить, как цены влияют на продажи — тогда усложните систему. Пока же — KISS (Keep It Simple, Stupid) 😊
