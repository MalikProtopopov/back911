# API запросы для страницы услуги в городе

## 📋 Обзор

Этот документ описывает правильные API запросы для получения данных на страницу услуги в конкретном городе (например, "Шиномонтаж в Москве").

---

## 🎯 Рекомендуемый подход

### Вариант 1: Основной эндпоинт (РЕКОМЕНДУЕТСЯ) ⭐

**URL Pattern:**
```
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

**Примеры:**
- `GET /api/website/cities/moskva/services/shinomontazh/` - шиномонтаж в Москве
- `GET /api/website/cities/sankt-peterburg/services/evakuator/` - эвакуатор в СПб
- `GET /api/website/cities/ekaterinburg/services/zapravka-toplivom/` - заправка в Екатеринбурге

**Что возвращает:**

```json
{
  "city": {
    "id": 63,
    "title": "Москва",
    "slug": "moskva",
    "partner_count": 150
  },
  "service": {
    "id": 1,
    "title": "Выездной шиномонтаж",
    "slug": "shinomontazh",
    "icon_url": "/static/icons/shinomontazh.svg",
    "options_count": 56
  },
  "options": [
    {
      "id": 1,
      "title": "Зарядка аккумулятора",
      "service_id": 1,
      "service_title": "Выездной шиномонтаж",
      "service_slug": "shinomontazh",
      "is_active": true,
      "price": {
        "amount": "500.00",
        "technic_category": "Грузовой автомобиль"
      }
    },
    // ... остальные опции
  ],
  "content": {
    "description": "<p>HTML контент с описанием услуги...</p>",
    "how_it_works_html": "<div>...</div>",
    "benefits_html": "<div>...</div>"
  },
  "seo": {
    "meta_title": "Шиномонтаж в Москве - 911",
    "meta_description": "...",
    "meta_keywords": "...",
    "og_title": "...",
    "og_description": "..."
  }
}
```

**✅ Преимущества:**
- **Один запрос** получает всё необходимое для страницы
- Возвращает информацию о городе, услуге, опциях с ценами, контент и SEO
- Оптимизирован для производительности
- Возвращает только опции с ценами в данном городе

**⚠️ Ограничение:**
- Для каждой опции возвращается **только одна цена** (первая найденная для данного города)
- Если у опции есть разные цены для разных категорий техники - вернется только одна

---

### Вариант 2: Раздельные запросы для полного контроля

Если тебе нужны **ВСЕ цены** для опции (по всем категориям техники), используй комбинацию запросов:

#### Шаг 1: Получить город и услугу

```bash
# Получить информацию о городе
GET /api/website/cities/{city_slug}/

# Получить информацию об услуге
GET /api/website/services/{service_slug}/
```

#### Шаг 2: Получить опции с ценами для города

```bash
GET /api/website/options/by-city/?city={city_slug}&service={service_slug}
```

**Пример:**
```bash
GET /api/website/options/by-city/?city=moskva&service=shinomontazh
```

**Что возвращает:**

```json
[
  {
    "id": 1,
    "title": "Зарядка аккумулятора",
    "service_id": 1,
    "service_title": "Выездной шиномонтаж",
    "service_slug": "shinomontazh",
    "is_active": true,
    "price": {
      "amount": "500.00",
      "technic_category": "Грузовой автомобиль"
    }
  },
  // ... остальные опции
]
```

**⚠️ Та же проблема:**
- Возвращает только **одну цену** на опцию для данного города

---

### Вариант 3: Получить ВСЕ цены по всем категориям техники

Если на странице нужно показать **все возможные цены** для опции (например, цену для легкового, кроссовера, внедорожника и т.д.), используй:

```bash
GET /api/website/options/{option_id}/
```

**Пример:**
```bash
GET /api/website/options/1/
```

**Что возвращает:**

```json
{
  "id": 1,
  "title": "Зарядка аккумулятора",
  "service_id": 1,
  "service_title": "Выездной шиномонтаж",
  "service_slug": "shinomontazh",
  "is_active": true,
  "prices": [
    {
      "id": 22,
      "city_slug": "pskov",
      "city_title": "Псков",
      "technic_category_id": 1,
      "technic_category_title": "Грузовой автомобиль",
      "amount": "1000.00"
    },
    {
      "id": 181,
      "city_slug": "moskva",
      "city_title": "Москва",
      "technic_category_id": 1,
      "technic_category_title": "Грузовой автомобиль",
      "amount": "500.00"
    },
    {
      "id": 182,
      "city_slug": "moskva",
      "city_title": "Москва",
      "technic_category_id": 2,
      "technic_category_title": "Легковой автомобиль",
      "amount": "300.00"
    },
    {
      "id": 183,
      "city_slug": "moskva",
      "city_title": "Москва",
      "technic_category_id": 3,
      "technic_category_title": "Кроссовер",
      "amount": "350.00"
    }
    // ... все цены по всем городам и категориям
  ]
}
```

**✅ Преимущества:**
- Возвращает **ВСЕ цены** для опции по всем городам и категориям техники
- Можно фильтровать на фронтенде по нужному городу

**❌ Недостатки:**
- Нужно делать **отдельный запрос для каждой опции**
- Много лишних данных (цены по другим городам)
- Неэффективно для страницы со списком опций

---

## 🎨 Рекомендуемая стратегия для фронтенда

### Сценарий 1: Простое отображение цен

Если нужно просто показать **одну базовую цену** для каждой опции:

```javascript
// 1. Один запрос для всей страницы
const response = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const data = await response.json();

// 2. Используй данные напрямую
console.log(data.city);      // Информация о городе
console.log(data.service);   // Информация об услуге
console.log(data.options);   // Опции с ценами
console.log(data.content);   // HTML контент
console.log(data.seo);       // SEO метаданные
```

---

### Сценарий 2: Отображение цен по категориям техники

Если нужно показать **разные цены** в зависимости от выбора пользователя (легковой/кроссовер/внедорожник):

#### Вариант A: Загрузить все сразу (при загрузке страницы)

```javascript
// 1. Получить основную информацию
const mainResponse = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const mainData = await mainResponse.json();

// 2. Для каждой опции получить все цены
const optionsWithAllPrices = await Promise.all(
  mainData.options.map(async (option) => {
    const priceResponse = await fetch(`/api/website/options/${option.id}/`);
    const priceData = await priceResponse.json();
    
    // Фильтровать только цены для Москвы
    const moscowPrices = priceData.prices.filter(
      price => price.city_slug === 'moskva'
    );
    
    return {
      ...option,
      allPrices: moscowPrices // Массив цен по категориям техники
    };
  })
);

// 3. Использовать optionsWithAllPrices для отображения
```

#### Вариант B: Lazy loading (при выборе опции)

```javascript
// 1. Показать страницу с базовыми ценами
const mainResponse = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const mainData = await mainResponse.json();

// 2. Когда пользователь выбирает опцию - загрузить детали
async function onOptionSelect(optionId) {
  const response = await fetch(`/api/website/options/${optionId}/`);
  const data = await response.json();
  
  // Показать все цены по категориям техники для Москвы
  const moscowPrices = data.prices.filter(
    price => price.city_slug === 'moskva'
  );
  
  return moscowPrices;
}
```

---

## 🔧 Текущая проблема и решение

### Проблема

Сейчас `OptionWithCityPriceSerializer` возвращает только **одну цену** на опцию:

```python
def get_price(self, obj):
    """Get price for the city from context"""
    city = self.context.get('city')
    price_query = obj.prices.filter(city=city)
    price = price_query.first()  # ⚠️ Берет только первую!
    
    if price:
        return {
            'amount': str(price.amount),
            'technic_category': price.technic_category.title if price.technic_category else None
        }
    return None
```

### Решение (если нужно изменить API)

Если хочешь, чтобы основной эндпоинт возвращал **все цены** для опции по категориям техники, нужно изменить сериализатор:

```python
class OptionWithAllCityPricesSerializer(serializers.ModelSerializer):
    """Option serializer with ALL prices for specific city"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'service_id',
            'service_title',
            'service_slug',
            'is_active',
            'prices',  # Теперь массив
        ]
    
    def get_prices(self, obj):
        """Get ALL prices for the city from context"""
        city = self.context.get('city')
        
        if not city:
            return []
        
        # Получить ВСЕ цены для города
        prices = obj.prices.filter(city=city)
        
        return [
            {
                'amount': str(price.amount),
                'technic_category_id': price.technic_category.id if price.technic_category else None,
                'technic_category': price.technic_category.title if price.technic_category else None
            }
            for price in prices
        ]
```

Тогда ответ будет таким:

```json
{
  "id": 1,
  "title": "Зарядка аккумулятора",
  "prices": [
    {"amount": "500.00", "technic_category_id": 1, "technic_category": "Грузовой автомобиль"},
    {"amount": "300.00", "technic_category_id": 2, "technic_category": "Легковой автомобиль"},
    {"amount": "350.00", "technic_category_id": 3, "technic_category": "Кроссовер"}
  ]
}
```

---

## 📊 Сравнение подходов

| Подход | Запросов | Данных | Гибкость | Сложность | Рекомендация |
|--------|----------|--------|----------|-----------|--------------|
| **Вариант 1**: Основной эндпоинт | 1 | Минимум | Низкая | Низкая | ⭐ Для простых страниц |
| **Вариант 2**: by-city | 2-3 | Средне | Средняя | Средняя | Если нужен контроль |
| **Вариант 3**: Детальные опции | N+1 | Много | Высокая | Высокая | ❌ Не рекомендуется |
| **Изменить API**: Новый сериализатор | 1 | Средне | Высокая | Низкая | ⭐ Оптимально |

---

## 🚀 Итоговые рекомендации

### Для текущей реализации:

1. **Используй основной эндпоинт** для базовой загрузки страницы:
   ```
   GET /api/website/cities/{city_slug}/services/{service_slug}/
   ```

2. **Если нужны цены по категориям** - добавь lazy loading:
   ```javascript
   // При клике на опцию/категорию техники
   GET /api/website/options/{option_id}/
   // и отфильтруй по city_slug на фронтенде
   ```

### Для улучшения API (рекомендую):

Измени `OptionWithCityPriceSerializer` чтобы поле `price` возвращало **массив** вместо одного объекта:

```javascript
// Вместо:
"price": {"amount": "500.00", "technic_category": "Грузовой"}

// Будет:
"prices": [
  {"amount": "500.00", "technic_category_id": 1, "technic_category": "Грузовой"},
  {"amount": "300.00", "technic_category_id": 2, "technic_category": "Легковой"},
  {"amount": "350.00", "technic_category_id": 3, "technic_category": "Кроссовер"}
]
```

Это даст фронтенду всю необходимую информацию в одном запросе! 🎯

---

## 🎯 Пример использования на фронтенде

```javascript
// Страница: /moskva/shinomontazh

// 1. Загрузка данных страницы
async function loadServicePage(citySlug, serviceSlug) {
  const response = await fetch(
    `/api/website/cities/${citySlug}/services/${serviceSlug}/`
  );
  const data = await response.json();
  
  return {
    city: data.city,
    service: data.service,
    options: data.options,
    content: data.content,
    seo: data.seo
  };
}

// 2. Использование
const page = await loadServicePage('moskva', 'shinomontazh');

// Установить SEO
document.title = page.seo?.meta_title || `${page.service.title} в ${page.city.title}`;

// Отобразить контент
document.querySelector('.service-description').innerHTML = page.content?.description;

// Отобразить опции с ценами
page.options.forEach(option => {
  console.log(`${option.title}: ${option.price.amount} руб.`);
  if (option.price.technic_category) {
    console.log(`Категория: ${option.price.technic_category}`);
  }
});
```

---

## 📝 Связанные документы

- [Анализ ценообразования опций](./OPTION_PRICING_ANALYSIS.md)
- [Техническая спецификация API](./BACKEND_TECHNICAL_SPECIFICATION.md)
- [OpenAPI схема](./911%20Corporate%20Website%20API%20(1).yaml)

---

**Дата создания:** 2025-12-27  
**Статус:** ✅ Актуально

