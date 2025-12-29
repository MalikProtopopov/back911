# API - Краткий справочник для фронтенда

## 🎯 Страница услуги в городе

### Один запрос для всей страницы (РЕКОМЕНДУЕТСЯ ⭐)

```bash
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

**Примеры:**
```bash
GET /api/website/cities/moskva/services/shinomontazh/
GET /api/website/cities/sankt-peterburg/services/evakuator/
GET /api/website/cities/ekaterinburg/services/zapravka-toplivom/
```

**Возвращает:**
- ✅ Информацию о городе (`city`)
- ✅ Информацию об услуге (`service`)
- ✅ Опции с ценами для данного города (`options[]`)
- ✅ HTML контент страницы (`content`)
- ✅ SEO метаданные (`seo`)

**Пример ответа:**
```json
{
  "city": {
    "id": 63,
    "title": "Москва",
    "slug": "moskva",
    "partner_count": 0
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
    }
  ],
  "content": {
    "description": "<p>Описание услуги...</p>",
    "how_it_works_html": "<div>...</div>",
    "benefits_html": "<div>...</div>"
  },
  "seo": {
    "meta_title": "Шиномонтаж в Москве - 911",
    "meta_description": "...",
    "og_title": "..."
  }
}
```

---

## ⚠️ Важная информация о ценах

### Текущее поведение

Каждая опция возвращает **только одну цену** в поле `price`:

```json
{
  "id": 1,
  "title": "Балансировка колеса",
  "price": {
    "amount": "500.00",
    "technic_category": "Грузовой автомобиль"  // Только одна категория!
  }
}
```

**Если у опции есть несколько цен** (для легкового, кроссовера, внедорожника) — возвращается только первая найденная.

### Получить все цены для опции

Если нужны **ВСЕ цены по всем категориям техники**:

```bash
GET /api/website/options/{option_id}/
```

**Пример:**
```bash
GET /api/website/options/1/
```

**Возвращает:**
```json
{
  "id": 1,
  "title": "Балансировка колеса",
  "service_id": 1,
  "service_title": "Выездной шиномонтаж",
  "service_slug": "shinomontazh",
  "is_active": true,
  "prices": [
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
    // + цены для других городов
  ]
}
```

**На фронтенде:**
```javascript
// Отфильтровать цены для Москвы
const moscowPrices = data.prices.filter(p => p.city_slug === 'moskva');
```

---

## 📊 Категории техники

Получить список категорий техники для услуги:

```bash
GET /api/website/technic-categories/?service__slug={service_slug}
```

**Пример:**
```bash
GET /api/website/technic-categories/?service__slug=shinomontazh
```

**Возвращает:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Грузовой автомобиль"
    },
    {
      "id": 3,
      "title": "Легковой автомобиль"
    }
  ]
}
```

---

## 🚀 Рекомендуемая стратегия

### Простой сценарий (одна цена на опцию)

```javascript
// Загрузить всю страницу одним запросом
const response = await fetch(
  '/api/website/cities/moskva/services/shinomontazh/'
);
const page = await response.json();

// Использовать данные
page.options.forEach(option => {
  console.log(`${option.title}: ${option.price.amount} руб.`);
});
```

### Сложный сценарий (цены по категориям техники)

```javascript
// 1. Загрузить основную страницу
const mainResponse = await fetch(
  '/api/website/cities/moskva/services/shinomontazh/'
);
const page = await mainResponse.json();

// 2. Загрузить категории техники
const categoriesResponse = await fetch(
  '/api/website/technic-categories/?service__slug=shinomontazh'
);
const categories = await categoriesResponse.json();

// 3. Для каждой опции получить все цены (если нужно)
async function loadOptionPrices(optionId) {
  const response = await fetch(`/api/website/options/${optionId}/`);
  const data = await response.json();
  
  // Отфильтровать цены для Москвы
  const cityPrices = data.prices.filter(p => p.city_slug === 'moskva');
  
  return cityPrices;
}

// 4. Пример: пользователь выбрал опцию
const optionPrices = await loadOptionPrices(1);
console.log('Цены по категориям:', optionPrices);
```

---

## 🔗 Альтернативные эндпоинты

### Опции по городу и услуге

```bash
GET /api/website/options/by-city/?city={city_slug}&service={service_slug}
```

**Пример:**
```bash
GET /api/website/options/by-city/?city=moskva&service=shinomontazh
```

**Возвращает:** Массив опций (без данных о городе, услуге, контенте, SEO)

**Когда использовать:**
- Если нужны только опции без других данных страницы
- ⚠️ Тоже возвращает только одну цену на опцию

---

## 📝 Итоговые рекомендации

| Задача | API запрос | Комментарий |
|--------|-----------|-------------|
| Загрузить страницу услуги в городе | `GET /cities/{city}/services/{service}/` | ⭐ Основной эндпоинт |
| Получить все цены для опции | `GET /options/{id}/` | Для детальной информации |
| Получить категории техники | `GET /technic-categories/?service__slug={slug}` | Для фильтрации цен |
| Только список опций | `GET /options/by-city/?city={city}&service={service}` | Альтернатива |

---

## 🐛 Известные ограничения

1. ⚠️ **Основной эндпоинт возвращает только одну цену на опцию** (первую найденную для города)
   - **Решение:** Использовать `GET /options/{id}/` для получения всех цен

2. ⚠️ **Нет эндпоинта для получения всех опций с ценами по категориям в одном запросе**
   - **Решение:** Либо делать N+1 запросов, либо изменить сериализатор (см. `API_USAGE_SERVICE_PAGE.md`)

---

## 📚 Дополнительная документация

- [Подробное руководство по API](./API_USAGE_SERVICE_PAGE.md) - Детальные примеры и стратегии
- [Анализ ценообразования опций](./OPTION_PRICING_ANALYSIS.md) - Как устроены цены в БД
- [OpenAPI схема](./911%20Corporate%20Website%20API%20(1).yaml) - Полная спецификация API

---

**Дата:** 2025-12-27  
**Статус:** ✅ Актуально

