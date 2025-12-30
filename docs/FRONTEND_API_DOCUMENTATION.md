# 📖 Документация API для фронтенда

## Версия: 2.0 (Обновление системы ценообразования)
**Дата:** 30.12.2025

---

## 📋 Содержание

1. [Обзор изменений](#обзор-изменений)
2. [Базовые URL](#базовые-url)
3. [Основные API endpoints](#основные-api-endpoints)
4. [Структура данных](#структура-данных)
5. [Логика расчёта цен](#логика-расчёта-цен)
6. [Пошаговый план обновления фронта](#пошаговый-план-обновления-фронта)
7. [Примеры использования](#примеры-использования)
8. [FAQ](#faq)

---

## 🔄 Обзор изменений

### Что изменилось:

| Было | Стало |
|------|-------|
| Опция имела фиксированную цену | Опция может иметь **параметры** (радиус шины, тип топлива) |
| Одна цена на опцию | **Базовая цена + модификатор параметра** |
| Нет зон доставки в API | Появился API **зон доставки** с ценами |
| Нет API расчёта цены | Появился endpoint `/api/pricing/calculate/` |

### Новые поля в опциях:

- `has_parameters` — флаг, имеет ли опция параметры
- `parameter_types` — массив типов параметров со значениями и ценами
- `parameter_prices` — цены параметров (сгруппированы по типу)

### Новые endpoints:

- `GET /api/pricing/parameter-types/` — типы параметров
- `GET /api/pricing/parameter-types/{code}/values/` — значения параметра
- `GET /api/pricing/cities/{city_id}/delivery-zones/` — зоны доставки
- `POST /api/pricing/calculate/` — расчёт итоговой цены

---

## 🌐 Базовые URL

```
Production: https://api.911.ru
Development: http://localhost:8001

API Base: /api/website/
Pricing API: /api/pricing/
```

---

## 📡 Основные API endpoints

### 1. Услуга в городе (главный endpoint)

```http
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

**Пример:** `GET /api/website/cities/moskva/services/vyezdnoj-shinomontazh/`

**Ответ:**
```json
{
  "city": {
    "id": 63,
    "title": "Москва",
    "slug": "moskva"
  },
  "service": {
    "id": 1,
    "title": "Выездной шиномонтаж",
    "slug": "vyezdnoj-shinomontazh",
    "icon_url": null
  },
  "options": [
    {
      "id": 45,
      "title": "Установка колеса",
      "description": "",
      "service_id": 1,
      "service_title": "Выездной шиномонтаж",
      "service_slug": "vyezdnoj-shinomontazh",
      "has_parameters": true,
      "parameter_types": [
        {
          "code": "radius",
          "title": "Радиус шины",
          "is_required": true,
          "values": [
            {"id": 5, "value": "r13", "display_name": "R13", "price_modifier": "0.00"},
            {"id": 6, "value": "r14", "display_name": "R14", "price_modifier": "0.00"},
            {"id": 7, "value": "r15", "display_name": "R15", "price_modifier": "0.00"},
            {"id": 8, "value": "r16", "display_name": "R16", "price_modifier": "0.00"},
            {"id": 9, "value": "r17", "display_name": "R17", "price_modifier": "300.00"},
            {"id": 10, "value": "r18", "display_name": "R18", "price_modifier": "300.00"},
            {"id": 11, "value": "r19", "display_name": "R19", "price_modifier": "500.00"},
            {"id": 12, "value": "r20", "display_name": "R20", "price_modifier": "500.00"},
            {"id": 13, "value": "r21", "display_name": "R21", "price_modifier": "800.00"},
            {"id": 14, "value": "r22", "display_name": "R22", "price_modifier": "800.00"}
          ]
        }
      ],
      "prices": [
        {"amount": "500.00", "technic_category": "Легковой автомобиль"},
        {"amount": "800.00", "technic_category": "Грузовой автомобиль"}
      ],
      "parameter_prices": {
        "radius": [
          {"value_id": 9, "display_name": "R17", "price_modifier": "300.00"},
          {"value_id": 10, "display_name": "R18", "price_modifier": "300.00"},
          {"value_id": 11, "display_name": "R19", "price_modifier": "500.00"}
        ]
      },
      "is_active": true
    },
    {
      "id": 2,
      "title": "Балансировка колеса",
      "description": "",
      "service_id": 1,
      "service_title": "Выездной шиномонтаж",
      "service_slug": "vyezdnoj-shinomontazh",
      "has_parameters": false,
      "parameter_types": [],
      "prices": [
        {"amount": "300.00", "technic_category": "Легковой автомобиль"},
        {"amount": "500.00", "technic_category": "Грузовой автомобиль"}
      ],
      "parameter_prices": {},
      "is_active": true
    }
  ],
  "content": {
    "meta_title": "Шиномонтаж в Москве",
    "meta_description": "Выездной шиномонтаж в Москве",
    "h1_title": "Шиномонтаж",
    "description": "<p>Описание услуги...</p>"
  },
  "seo": null
}
```

---

### 2. Опции услуги (с фильтрацией)

```http
GET /api/website/cities/{city_slug}/services/{service_slug}/options/
GET /api/website/cities/{city_slug}/services/{service_slug}/options/?technic_category=1
GET /api/website/cities/{city_slug}/services/{service_slug}/options/?technic_category__title=Грузовой автомобиль
```

**Query параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `technic_category` | int | ID категории техники для фильтрации |
| `technic_category__title` | string | Название категории для фильтрации |

---

### 3. Категории техники

```http
GET /api/website/technic-categories/
```

**Ответ:**
```json
{
  "count": 8,
  "results": [
    {"id": 1, "title": "Легковой автомобиль", "slug": "legkovoj-avtomobil"},
    {"id": 2, "title": "Грузовой автомобиль", "slug": "gruzovoj-avtomobil"},
    {"id": 3, "title": "Генератор", "slug": "generator"},
    {"id": 4, "title": "Паром", "slug": "parom"},
    {"id": 5, "title": "Гидроцикл", "slug": "gidratsikl"},
    {"id": 6, "title": "Вилочный погрузчик", "slug": "vilochnyj-pogruzchik"},
    {"id": 7, "title": "Каток", "slug": "katok"},
    {"id": 8, "title": "Экскаватор", "slug": "ekskavator"}
  ]
}
```

---

### 4. Типы параметров

```http
GET /api/pricing/parameter-types/
```

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "code": "fuel_type",
      "title": "Тип топлива",
      "description": "",
      "values_count": 4
    },
    {
      "id": 2,
      "code": "radius",
      "title": "Радиус шины",
      "description": "",
      "values_count": 23
    }
  ]
}
```

---

### 5. Значения параметра

```http
GET /api/pricing/parameter-types/{code}/values/
```

**Пример:** `GET /api/pricing/parameter-types/radius/values/`

**Ответ:**
```json
{
  "count": 23,
  "results": [
    {"id": 5, "value": "r13", "display_name": "R13", "sort_order": 0},
    {"id": 6, "value": "r14", "display_name": "R14", "sort_order": 1},
    {"id": 7, "value": "r15", "display_name": "R15", "sort_order": 2},
    {"id": 8, "value": "r16", "display_name": "R16", "sort_order": 3},
    {"id": 9, "value": "r17", "display_name": "R17", "sort_order": 4},
    {"id": 10, "value": "r18", "display_name": "R18", "sort_order": 5},
    {"id": 11, "value": "r19", "display_name": "R19", "sort_order": 6}
  ]
}
```

---

### 6. Зоны доставки

```http
GET /api/pricing/cities/{city_id}/delivery-zones/
```

**Пример:** `GET /api/pricing/cities/63/delivery-zones/`

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "zone_name": "В городе",
      "location_status": "in_city",
      "delivery_price": "2000.00"
    },
    {
      "id": 2,
      "zone_name": "За городом",
      "location_status": "out_city",
      "delivery_price": "2500.00"
    }
  ]
}
```

---

### 7. Расчёт цены (POST)

```http
POST /api/pricing/calculate/
```

**Тело запроса:**
```json
{
  "option_id": 45,
  "city_id": 63,
  "technic_category_id": 1,
  "parameter_values": {
    "radius": 11
  },
  "delivery_zone_id": 2
}
```

**Ответ:**
```json
{
  "base_price": "500.00",
  "parameters_price": "500.00",
  "delivery_price": "2500.00",
  "total_price": "3500.00",
  "breakdown": [
    {"type": "base", "label": "Установка колеса", "amount": "500.00"},
    {"type": "parameter", "label": "R19", "amount": "500.00"},
    {"type": "delivery", "label": "За городом", "amount": "2500.00"}
  ]
}
```

---

## 📊 Структура данных

### Опция (Option)

```typescript
interface Option {
  id: number
  title: string
  description: string
  service_id: number
  service_title: string
  service_slug: string
  
  // ✨ НОВОЕ: Флаг наличия параметров
  has_parameters: boolean
  
  // ✨ НОВОЕ: Типы параметров с их значениями и ценами
  parameter_types: ParameterType[]
  
  // Базовые цены (без параметров)
  prices: OptionPrice[]
  
  // ✨ НОВОЕ: Цены параметров, сгруппированные по типу
  parameter_prices: Record<string, ParameterPriceItem[]>
  
  is_active: boolean
}
```

### Тип параметра (ParameterType)

```typescript
interface ParameterType {
  code: string         // "radius", "fuel_type"
  title: string        // "Радиус шины", "Тип топлива"
  is_required: boolean // true = обязательно выбрать
  values: ParameterValue[]
}
```

### Значение параметра (ParameterValue)

```typescript
interface ParameterValue {
  id: number
  value: string         // "r15", "ai92"
  display_name: string  // "R15", "АИ-92"
  price_modifier: string // "300.00" — надбавка к базовой цене
}
```

### Цена опции (OptionPrice)

```typescript
interface OptionPrice {
  amount: string              // "500.00"
  technic_category: string | null // "Легковой автомобиль" или null
}
```

### Цена параметра (ParameterPriceItem)

```typescript
interface ParameterPriceItem {
  value_id: number       // ID значения параметра
  display_name: string   // "R19"
  price_modifier: string // "500.00" — надбавка
}
```

---

## 💰 Логика расчёта цен

### ⚠️ ВАЖНО: Как считать итоговую цену

**Формула:**
```
Итого = Базовая цена опции + Модификатор параметра + Цена доставки
```

### Пример расчёта:

| Компонент | Значение |
|-----------|----------|
| Базовая цена "Установка колеса" (Легковой) | 500 ₽ |
| Модификатор "R19" | +500 ₽ |
| Доставка "За городом" | +2500 ₽ |
| **ИТОГО** | **3500 ₽** |

### Правила отображения на фронте:

#### 1️⃣ Опция БЕЗ параметров (`has_parameters: false`)

Показываем просто базовую цену из `prices`:

```
┌─────────────────────────────────┐
│ Балансировка колеса      300 ₽ │ (Легковой)
│ Балансировка колеса      500 ₽ │ (Грузовой)
└─────────────────────────────────┘
```

#### 2️⃣ Опция С параметрами (`has_parameters: true`)

**Вариант A: Показать диапазон цен**
```
┌─────────────────────────────────────┐
│ Установка колеса      от 500 ₽     │
│   └── Выберите радиус (R13-R22)    │
└─────────────────────────────────────┘
```

**Вариант B: Показать аккордеон с параметрами**
```
┌─────────────────────────────────────┐
│ ▼ Установка колеса (Легковой)      │
├─────────────────────────────────────┤
│   R13 - R16     500 ₽              │
│   R17 - R18     800 ₽  (+300 ₽)    │
│   R19 - R20     1000 ₽ (+500 ₽)    │
│   R21 - R22     1300 ₽ (+800 ₽)    │
└─────────────────────────────────────┘
```

### Откуда брать данные:

| Что нужно | Откуда брать |
|-----------|--------------|
| Базовая цена | `option.prices[].amount` |
| Категория техники | `option.prices[].technic_category` |
| Надбавка за параметр | `option.parameter_types[].values[].price_modifier` |
| Итоговая цена | Базовая + price_modifier |

### Пример кода расчёта:

```typescript
function calculateOptionPrice(
  option: Option,
  technicCategory: string,
  selectedParameterValueId?: number
): number {
  // 1. Находим базовую цену для категории
  const basePrice = option.prices.find(
    p => p.technic_category === technicCategory
  )
  
  if (!basePrice) return 0
  
  let total = parseFloat(basePrice.amount)
  
  // 2. Если опция имеет параметры и выбрано значение
  if (option.has_parameters && selectedParameterValueId) {
    for (const paramType of option.parameter_types) {
      const selectedValue = paramType.values.find(
        v => v.id === selectedParameterValueId
      )
      if (selectedValue) {
        total += parseFloat(selectedValue.price_modifier)
      }
    }
  }
  
  return total
}
```

---

## 📝 Пошаговый план обновления фронта

### Шаг 1: Обновить TypeScript типы

Добавить новые интерфейсы в `types/`:

```typescript
// types/option.ts

export interface ParameterValue {
  id: number
  value: string
  display_name: string
  price_modifier: string
}

export interface ParameterType {
  code: string
  title: string
  is_required: boolean
  values: ParameterValue[]
}

export interface Option {
  id: number
  title: string
  description: string
  service_id: number
  service_title: string
  service_slug: string
  has_parameters: boolean              // ✨ НОВОЕ
  parameter_types: ParameterType[]     // ✨ НОВОЕ
  prices: OptionPrice[]
  parameter_prices: Record<string, ParameterPriceItem[]> // ✨ НОВОЕ
  is_active: boolean
}
```

### Шаг 2: Обновить API сервис

Добавить методы для Pricing API:

```typescript
// services/pricingService.ts

export const pricingService = {
  // Получить типы параметров
  async getParameterTypes() {
    const response = await api.get('/api/pricing/parameter-types/')
    return response.data.results
  },
  
  // Получить значения параметра
  async getParameterValues(code: string) {
    const response = await api.get(`/api/pricing/parameter-types/${code}/values/`)
    return response.data.results
  },
  
  // Получить зоны доставки
  async getDeliveryZones(cityId: number) {
    const response = await api.get(`/api/pricing/cities/${cityId}/delivery-zones/`)
    return response.data.results
  },
  
  // Расчёт цены
  async calculatePrice(params: {
    option_id: number
    city_id: number
    technic_category_id?: number
    parameter_values?: Record<string, number>
    delivery_zone_id?: number
  }) {
    const response = await api.post('/api/pricing/calculate/', params)
    return response.data
  }
}
```

### Шаг 3: Обновить компонент PriceAccordion

**Логика группировки опций:**

```typescript
function groupOptions(options: Option[]) {
  const groups: Record<string, Option[]> = {}
  
  for (const option of options) {
    // Группируем по категории техники из prices
    for (const price of option.prices) {
      const category = price.technic_category || 'Прочие услуги'
      
      if (!groups[category]) {
        groups[category] = []
      }
      
      // Добавляем опцию в группу (если ещё не добавлена)
      if (!groups[category].find(o => o.id === option.id)) {
        groups[category].push(option)
      }
    }
  }
  
  return groups
}
```

### Шаг 4: Создать компонент OptionRow

```tsx
// components/OptionRow.tsx

interface OptionRowProps {
  option: Option
  technicCategory: string
}

export function OptionRow({ option, technicCategory }: OptionRowProps) {
  // Находим базовую цену для этой категории
  const basePrice = option.prices.find(
    p => p.technic_category === technicCategory
  )
  
  if (!basePrice) return null
  
  // Если опция БЕЗ параметров — просто показываем цену
  if (!option.has_parameters) {
    return (
      <div className="option-row">
        <span>{option.title}</span>
        <span>{formatPrice(basePrice.amount)} ₽</span>
      </div>
    )
  }
  
  // Если опция С параметрами — показываем подсписок
  return (
    <div className="option-row expandable">
      <div className="option-header">
        <span>{option.title}</span>
        <span>от {formatPrice(basePrice.amount)} ₽</span>
      </div>
      
      <div className="option-parameters">
        {option.parameter_types.map(paramType => (
          <div key={paramType.code} className="parameter-group">
            <span className="parameter-title">{paramType.title}:</span>
            {paramType.values.map(value => {
              const total = parseFloat(basePrice.amount) + parseFloat(value.price_modifier)
              const modifier = parseFloat(value.price_modifier)
              
              return (
                <div key={value.id} className="parameter-value">
                  <span>{value.display_name}</span>
                  <span>
                    {formatPrice(total)} ₽
                    {modifier > 0 && (
                      <span className="modifier">(+{formatPrice(modifier)})</span>
                    )}
                  </span>
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Шаг 5: Обновить страницу услуги

```tsx
// pages/[city]/[service]/page.tsx

export default async function ServicePage({ params }) {
  const { city, service } = params
  
  // Получаем данные (без изменений в API вызове)
  const data = await citiesService.getServiceByCity(city, service)
  
  // Группируем опции по категориям техники
  const groupedOptions = groupOptions(data.options)
  
  return (
    <div>
      <h1>{data.content?.h1_title || data.service.title}</h1>
      
      {/* Аккордеон с категориями */}
      <PriceAccordion>
        {Object.entries(groupedOptions).map(([category, options]) => (
          <PriceAccordionCategory key={category} title={category}>
            {options.map(option => (
              <OptionRow 
                key={option.id}
                option={option}
                technicCategory={category}
              />
            ))}
          </PriceAccordionCategory>
        ))}
      </PriceAccordion>
    </div>
  )
}
```

---

## 🤔 FAQ

### Q: Нужно ли на фронте складывать цены?

**A: ДА**, для отображения в прайс-листе нужно складывать:

```
Итоговая цена = base_price.amount + parameter_value.price_modifier
```

Бэкенд НЕ возвращает готовые суммы в списке — он возвращает отдельно базовую цену и модификаторы. Фронт должен сам рассчитать итог для отображения.

Если нужно проверить расчёт или получить детализацию — используйте `POST /api/pricing/calculate/`.

---

### Q: Что делать, если price_modifier = "0.00"?

**A:** Это означает, что выбор этого параметра бесплатный. Показывайте только базовую цену без модификатора.

```
R13 - R16     500 ₽         (modifier = 0)
R17 - R18     800 ₽ (+300)  (modifier = 300)
```

---

### Q: Что если prices пустой массив?

**A:** Это означает, что для данной опции нет цены в этом городе. Показывайте "По запросу" или скрывайте опцию.

---

### Q: Что если parameter_types пустой при has_parameters: true?

**A:** Это баг в данных. В норме если `has_parameters: true`, то `parameter_types` должен содержать хотя бы один тип параметра.

---

### Q: Как понять, какие параметры обязательные?

**A:** Поле `is_required` в `parameter_types[].is_required`:
- `true` — пользователь ОБЯЗАН выбрать значение
- `false` — необязательно

---

### Q: Как показать зоны доставки?

**A:** Получите зоны через `GET /api/pricing/cities/{city_id}/delivery-zones/` и покажите как выпадающий список:

```
Зона выезда:
  ○ В городе — 2000 ₽
  ○ За городом — 2500 ₽
```

---

## 📞 Поддержка

- Swagger UI: `http://localhost:8001/api/docs/`
- ReDoc: `http://localhost:8001/api/redoc/`
- OpenAPI Schema: `http://localhost:8001/api/schema/`

---

## 🔄 История изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.0 | 30.12.2025 | Добавлена система параметров ценообразования |
| 1.0 | - | Начальная версия |

