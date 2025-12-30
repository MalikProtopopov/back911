# Изменения API для фронтенда

## Обзор изменений

Добавлена система динамического ценообразования с параметрами. Все существующие endpoints **сохраняют обратную совместимость**, но получают новые поля.

---

## Изменения в существующих endpoints

### 1. GET /api/website/options/

**БЫЛО:**
```json
{
    "count": 77,
    "results": [
        {
            "id": 1,
            "title": "Замена колеса",
            "service_id": 1,
            "service_title": "Шиномонтаж",
            "service_slug": "shinomontazh",
            "is_active": true
        }
    ]
}
```

**СТАЛО:**
```json
{
    "count": 77,
    "results": [
        {
            "id": 1,
            "title": "Замена колеса",
            "description": "Замена колеса на месте",
            "service_id": 1,
            "service_title": "Шиномонтаж",
            "service_slug": "shinomontazh",
            "has_parameters": true,
            "parameter_types": [
                {
                    "code": "tire_radius",
                    "title": "Радиус шины",
                    "is_required": true
                }
            ],
            "is_active": true
        }
    ]
}
```

**Новые поля:**
- `description` (string) — описание опции
- `has_parameters` (boolean) — есть ли у опции параметры
- `parameter_types` (array) — типы параметров, если `has_parameters=true`

---

### 2. GET /api/website/options/{id}/

**БЫЛО:**
```json
{
    "id": 1,
    "title": "Замена колеса",
    "service_id": 1,
    "service_title": "Шиномонтаж",
    "service_slug": "shinomontazh",
    "is_active": true,
    "prices": [
        {
            "id": 1,
            "city_slug": "makhachkala",
            "city_title": "Махачкала",
            "technic_category_id": null,
            "technic_category_title": null,
            "amount": "200.00"
        }
    ]
}
```

**СТАЛО:**
```json
{
    "id": 1,
    "title": "Замена колеса",
    "description": "Замена колеса на месте",
    "service_id": 1,
    "service_title": "Шиномонтаж",
    "service_slug": "shinomontazh",
    "has_parameters": true,
    "parameter_types": [
        {
            "code": "tire_radius",
            "title": "Радиус шины",
            "is_required": true,
            "values": [
                {"id": 1, "value": "R13", "display_name": "R13"},
                {"id": 2, "value": "R14", "display_name": "R14"},
                {"id": 7, "value": "R19", "display_name": "R19"}
            ]
        }
    ],
    "is_active": true,
    "prices": [
        {
            "id": 1,
            "city_slug": "makhachkala",
            "city_title": "Махачкала",
            "technic_category_id": null,
            "technic_category_title": null,
            "amount": "200.00"
        }
    ]
}
```

---

### 3. GET /api/website/options/by-city/?city=makhachkala

**БЫЛО:**
```json
[
    {
        "id": 1,
        "title": "Замена колеса",
        "service_id": 1,
        "service_title": "Шиномонтаж",
        "service_slug": "shinomontazh",
        "is_active": true,
        "prices": [
            {"amount": "200.00", "technic_category": null}
        ]
    }
]
```

**СТАЛО:**
```json
[
    {
        "id": 1,
        "title": "Замена колеса",
        "description": "Замена колеса на месте",
        "service_id": 1,
        "service_title": "Шиномонтаж",
        "service_slug": "shinomontazh",
        "has_parameters": true,
        "parameter_types": [
            {
                "code": "tire_radius",
                "title": "Радиус шины",
                "is_required": true,
                "values": [
                    {"id": 1, "value": "R13", "display_name": "R13", "price_modifier": "0.00"},
                    {"id": 2, "value": "R14", "display_name": "R14", "price_modifier": "100.00"},
                    {"id": 7, "value": "R19", "display_name": "R19", "price_modifier": "500.00"}
                ]
            }
        ],
        "is_active": true,
        "prices": [
            {"amount": "200.00", "technic_category": null}
        ],
        "parameter_prices": {
            "tire_radius": [
                {"value_id": 1, "display_name": "R13", "price_modifier": "0.00"},
                {"value_id": 2, "display_name": "R14", "price_modifier": "100.00"},
                {"value_id": 7, "display_name": "R19", "price_modifier": "500.00"}
            ]
        }
    }
]
```

**Новые поля:**
- `parameter_types[].values` — значения с ценами для города
- `parameter_prices` — цены параметров, сгруппированные по типу

---

### 4. GET /api/website/cities/{slug}/

**БЫЛО:**
```json
{
    "id": 1,
    "title": "Махачкала",
    "slug": "makhachkala",
    "is_active": true
}
```

**СТАЛО:**
```json
{
    "id": 1,
    "title": "Махачкала",
    "slug": "makhachkala",
    "is_active": true,
    "delivery_zones": [
        {
            "id": 1,
            "zone_name": "В городе",
            "location_status": "in_city",
            "delivery_price": "0.00"
        },
        {
            "id": 2,
            "zone_name": "За городом",
            "location_status": "out_city",
            "delivery_price": "1500.00"
        }
    ]
}
```

**Новые поля:**
- `delivery_zones` (array) — зоны доставки с ценами

---

### 5. GET /api/website/cities/{city}/services/{service}/

**БЫЛО:**
```json
{
    "city": {...},
    "service": {...},
    "options": [...],
    "content": {...},
    "seo": {...}
}
```

**СТАЛО:**
```json
{
    "city": {
        "id": 1,
        "title": "Махачкала",
        "slug": "makhachkala",
        "delivery_zones": [
            {"id": 1, "zone_name": "В городе", "location_status": "in_city", "delivery_price": "0.00"},
            {"id": 2, "zone_name": "За городом", "location_status": "out_city", "delivery_price": "1500.00"}
        ]
    },
    "service": {...},
    "options": [
        {
            "id": 1,
            "title": "Замена колеса",
            "description": "...",
            "has_parameters": true,
            "parameter_types": [...],
            "prices": [...],
            "parameter_prices": {...}
        }
    ],
    "content": {...},
    "seo": {...}
}
```

---

## Новые endpoints

### 1. GET /api/pricing/parameter-types/

**Описание:** Список всех типов параметров

**Запрос:**
```
GET /api/pricing/parameter-types/
GET /api/pricing/parameter-types/?limit=10&offset=0
```

**Ответ:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "code": "tire_radius",
            "title": "Радиус шины",
            "description": "Выберите радиус колеса",
            "values_count": 10
        },
        {
            "id": 2,
            "code": "oil_type",
            "title": "Тип масла",
            "description": "Выберите тип масла для замены",
            "values_count": 5
        },
        {
            "id": 3,
            "code": "fuel_type",
            "title": "Тип топлива",
            "description": "Выберите тип топлива",
            "values_count": 4
        }
    ]
}
```

---

### 2. GET /api/pricing/parameter-types/{code}/values/

**Описание:** Значения конкретного типа параметра

**Запрос:**
```
GET /api/pricing/parameter-types/tire_radius/values/
GET /api/pricing/parameter-types/tire_radius/values/?limit=10&offset=0
```

**Ответ:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {"id": 1, "value": "R13", "display_name": "R13", "sort_order": 1},
        {"id": 2, "value": "R14", "display_name": "R14", "sort_order": 2},
        {"id": 3, "value": "R15", "display_name": "R15", "sort_order": 3},
        {"id": 4, "value": "R16", "display_name": "R16", "sort_order": 4},
        {"id": 5, "value": "R17", "display_name": "R17", "sort_order": 5},
        {"id": 6, "value": "R18", "display_name": "R18", "sort_order": 6},
        {"id": 7, "value": "R19", "display_name": "R19", "sort_order": 7},
        {"id": 8, "value": "R20", "display_name": "R20", "sort_order": 8},
        {"id": 9, "value": "R21", "display_name": "R21", "sort_order": 9},
        {"id": 10, "value": "R22", "display_name": "R22", "sort_order": 10}
    ]
}
```

---

### 3. GET /api/pricing/cities/{city_id}/delivery-zones/

**Описание:** Зоны доставки для города

**Запрос:**
```
GET /api/pricing/cities/1/delivery-zones/
```

**Ответ:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "zone_name": "В городе",
            "location_status": "in_city",
            "delivery_price": "0.00"
        },
        {
            "id": 2,
            "zone_name": "За городом",
            "location_status": "out_city",
            "delivery_price": "1500.00"
        }
    ]
}
```

---

### 4. POST /api/pricing/calculate/

**Описание:** Расчет итоговой цены

**Запрос:**
```json
POST /api/pricing/calculate/
Content-Type: application/json

{
    "option_id": 1,
    "city_id": 1,
    "technic_category_id": null,
    "parameter_values": {
        "tire_radius": 7
    },
    "delivery_zone_id": 2
}
```

**Параметры:**
- `option_id` (int, обязательный) — ID опции
- `city_id` (int, обязательный) — ID города
- `technic_category_id` (int, опциональный) — ID категории техники
- `parameter_values` (object, опциональный) — словарь {код_типа: id_значения}
- `delivery_zone_id` (int, опциональный) — ID зоны доставки

**Ответ:**
```json
{
    "base_price": "200.00",
    "parameters_price": "500.00",
    "delivery_price": "1500.00",
    "total_price": "2200.00",
    "breakdown": [
        {"type": "base", "label": "Замена колеса", "amount": "200.00"},
        {"type": "parameter", "label": "R19", "amount": "500.00"},
        {"type": "delivery", "label": "За городом", "amount": "1500.00"}
    ]
}
```

**Поля ответа:**
- `base_price` — базовая цена опции
- `parameters_price` — сумма модификаторов параметров
- `delivery_price` — цена доставки
- `total_price` — итоговая цена
- `breakdown` — разбивка расчета

---

## Логика работы на фронтенде

### Сценарий 1: Опция БЕЗ параметров

```javascript
// Опция с has_parameters=false
const option = {
    id: 1,
    title: "Эвакуатор",
    has_parameters: false,
    prices: [{ amount: "2500.00" }]
};

// Цена = базовая цена + доставка
const basePrice = parseFloat(option.prices[0].amount);
const deliveryPrice = 1500; // Из delivery_zones
const totalPrice = basePrice + deliveryPrice; // 4000 ₽
```

### Сценарий 2: Опция С параметрами

```javascript
// Опция с has_parameters=true
const option = {
    id: 2,
    title: "Замена колеса",
    has_parameters: true,
    prices: [{ amount: "200.00" }],
    parameter_types: [
        {
            code: "tire_radius",
            title: "Радиус шины",
            is_required: true,
            values: [
                { id: 1, value: "R13", price_modifier: "0.00" },
                { id: 7, value: "R19", price_modifier: "500.00" }
            ]
        }
    ]
};

// Пользователь выбрал R19
const selectedRadius = 7; // id значения

// Локальный расчет:
const basePrice = parseFloat(option.prices[0].amount); // 200
const radiusModifier = parseFloat(
    option.parameter_types[0].values.find(v => v.id === 7).price_modifier
); // 500
const deliveryPrice = 1500;
const totalPrice = basePrice + radiusModifier + deliveryPrice; // 2200 ₽

// ИЛИ через API:
const response = await fetch('/api/pricing/calculate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        option_id: 2,
        city_id: 1,
        parameter_values: { tire_radius: 7 },
        delivery_zone_id: 2
    })
});
const result = await response.json();
// result.total_price = "2200.00"
```

---

## Пагинация

Все endpoints используют **LimitOffset пагинацию**:

```
GET /api/website/options/?limit=10&offset=0
GET /api/pricing/parameter-types/?limit=10&offset=0
```

**Формат ответа:**
```json
{
    "count": 77,
    "next": "http://api.example.com/api/website/options/?limit=10&offset=10",
    "previous": null,
    "results": [...]
}
```

**Если limit/offset не указаны** — возвращаются все записи.

---

## Обратная совместимость

Все существующие endpoints продолжают работать. Новые поля добавляются без изменения структуры.

**Для опций без параметров:**
- `has_parameters` = `false`
- `parameter_types` = `[]`
- `parameter_prices` = `{}`

Фронтенд может проверять `has_parameters` и показывать UI выбора параметров только когда это нужно.

---

## Пример: Калькулятор на фронтенде

```javascript
class PriceCalculator {
    constructor(apiBase) {
        this.apiBase = apiBase;
    }
    
    async loadCityData(citySlug) {
        // Загружаем город с зонами доставки
        const response = await fetch(`${this.apiBase}/api/website/cities/${citySlug}/`);
        return await response.json();
    }
    
    async loadServiceOptions(citySlug, serviceSlug) {
        // Загружаем опции услуги в городе
        const response = await fetch(
            `${this.apiBase}/api/website/cities/${citySlug}/services/${serviceSlug}/`
        );
        return await response.json();
    }
    
    calculateLocalPrice(option, parameterSelections, deliveryZone) {
        // Локальный расчет цены
        let total = parseFloat(option.prices[0]?.amount || 0);
        
        // Добавляем модификаторы параметров
        if (option.has_parameters && parameterSelections) {
            for (const [typeCode, valueId] of Object.entries(parameterSelections)) {
                const paramType = option.parameter_types.find(pt => pt.code === typeCode);
                if (paramType) {
                    const value = paramType.values.find(v => v.id === valueId);
                    if (value) {
                        total += parseFloat(value.price_modifier || 0);
                    }
                }
            }
        }
        
        // Добавляем доставку
        if (deliveryZone) {
            total += parseFloat(deliveryZone.delivery_price || 0);
        }
        
        return total;
    }
    
    async calculateServerPrice(optionId, cityId, parameterValues, deliveryZoneId) {
        // Серверный расчет цены
        const response = await fetch(`${this.apiBase}/api/pricing/calculate/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                option_id: optionId,
                city_id: cityId,
                parameter_values: parameterValues,
                delivery_zone_id: deliveryZoneId
            })
        });
        return await response.json();
    }
}
```

---

## Вопросы?

Если есть вопросы по интеграции — создайте issue или обратитесь к бэкенд-разработчику.

