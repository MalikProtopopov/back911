# API для аккордеона со списком цен опций услуги

## 📋 Обзор

Этот документ описывает API запросы для создания аккордеона со списком цен опций услуги внутри города с фильтром по категориям техники.

---

## 🎯 Основной эндпоинт для детальной страницы

### GET `/api/website/cities/{city_slug}/services/{service_slug}/`

**Описание:**  
Основной эндпоинт для получения информации об услуге в конкретном городе. Возвращает базовую информацию об опциях, но **только одну цену** на опцию.

**Пример:**
```bash
GET /api/website/cities/moskva/services/shinomontazh/
```

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
    "slug": "shinomontazh"
  },
  "options": [
    {
      "id": 1,
      "title": "Балансировка колеса",
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
  "content": { ... },
  "seo": { ... }
}
```

**⚠️ Важно:**  
Этот эндпоинт возвращает **только одну цену** на опцию (первую найденную). Если у опции есть разные цены для разных категорий техники, вернется только одна.

---

## 📊 Получение всех цен для опций

### GET `/api/website/options/{option_id}/`

**Описание:**  
Получить детальную информацию об опции со **всеми ценами** по всем городам и категориям техники.

**Пример:**
```bash
GET /api/website/options/1/
```

**Ответ:**
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
    },
    {
      "id": 184,
      "city_slug": "sankt-peterburg",
      "city_title": "Санкт-Петербург",
      "technic_category_id": 1,
      "technic_category_title": "Грузовой автомобиль",
      "amount": "550.00"
    }
  ]
}
```

**Поля ответа:**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | ID опции |
| `title` | string | Название опции |
| `service_id` | integer | ID услуги |
| `service_title` | string | Название услуги |
| `service_slug` | string | Slug услуги |
| `is_active` | boolean | Активна ли опция |
| `prices` | array | Массив всех цен опции |

**Поля объекта цены (`prices[]`):**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | ID цены |
| `city_slug` | string | Slug города |
| `city_title` | string | Название города |
| `technic_category_id` | integer\|null | ID категории техники (null если цена без категории) |
| `technic_category_title` | string\|null | Название категории техники (null если цена без категории) |
| `amount` | string | Цена (в формате "500.00") |

---

## 🚗 Получение категорий техники

### GET `/api/website/technic-categories/?service__slug={service_slug}`

**Описание:**  
Получить список всех категорий техники для конкретной услуги. Используется для создания фильтра в аккордеоне.

**Пример:**
```bash
GET /api/website/technic-categories/?service__slug=shinomontazh
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
      "title": "Грузовой автомобиль"
    },
    {
      "id": 2,
      "title": "Легковой автомобиль"
    },
    {
      "id": 3,
      "title": "Кроссовер"
    }
  ]
}
```

**Поля ответа:**

| Поле | Тип | Описание |
|------|-----|----------|
| `count` | integer | Общее количество категорий |
| `results` | array | Массив категорий техники |

**Поля объекта категории (`results[]`):**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | ID категории техники |
| `title` | string | Название категории техники |

---

## 🎨 Рекомендуемый подход для аккордеона

### Шаг 1: Получить базовую информацию об услуге в городе

```javascript
// Получить список опций с базовой информацией
const response = await fetch(
  `/api/website/cities/${citySlug}/services/${serviceSlug}/`
);
const data = await response.json();

// data.options - массив опций с одной ценой каждая
// data.city - информация о городе
// data.service - информация об услуге
```

### Шаг 2: Получить все цены для каждой опции

```javascript
// Для каждой опции получить все цены
const optionsWithPrices = await Promise.all(
  data.options.map(async (option) => {
    const optionResponse = await fetch(
      `/api/website/options/${option.id}/`
    );
    const optionData = await optionResponse.json();
    
    // Отфильтровать цены только для текущего города
    const cityPrices = optionData.prices.filter(
      price => price.city_slug === citySlug
    );
    
    return {
      ...option,
      prices: cityPrices  // Теперь массив всех цен для города
    };
  })
);
```

### Шаг 3: Получить категории техники для фильтра

```javascript
// Получить список категорий техники
const categoriesResponse = await fetch(
  `/api/website/technic-categories/?service__slug=${serviceSlug}`
);
const categoriesData = await categoriesResponse.json();

// categoriesData.results - массив категорий техники
```

---

## 📝 Пример полной реализации

```javascript
async function loadServicePageData(citySlug, serviceSlug) {
  // 1. Получить базовую информацию
  const baseResponse = await fetch(
    `/api/website/cities/${citySlug}/services/${serviceSlug}/`
  );
  const baseData = await baseResponse.json();
  
  // 2. Получить категории техники для фильтра
  const categoriesResponse = await fetch(
    `/api/website/technic-categories/?service__slug=${serviceSlug}`
  );
  const categoriesData = await categoriesResponse.json();
  
  // 3. Получить все цены для каждой опции
  const optionsWithAllPrices = await Promise.all(
    baseData.options.map(async (option) => {
      const optionResponse = await fetch(
        `/api/website/options/${option.id}/`
      );
      const optionData = await optionResponse.json();
      
      // Отфильтровать цены только для текущего города
      const cityPrices = optionData.prices.filter(
        price => price.city_slug === citySlug
      );
      
      return {
        id: option.id,
        title: option.title,
        service_id: option.service_id,
        service_title: option.service_title,
        service_slug: option.service_slug,
        is_active: option.is_active,
        prices: cityPrices  // Массив всех цен для города
      };
    })
  );
  
  return {
    city: baseData.city,
    service: baseData.service,
    content: baseData.content,
    seo: baseData.seo,
    options: optionsWithAllPrices,
    technicCategories: categoriesData.results
  };
}

// Использование
const pageData = await loadServicePageData('moskva', 'shinomontazh');

// pageData.options - массив опций, каждая с массивом цен
// pageData.technicCategories - массив категорий техники для фильтра
```

---

## 🎯 Структура данных для аккордеона

После загрузки данных структура будет следующей:

```javascript
{
  city: {
    id: 63,
    title: "Москва",
    slug: "moskva"
  },
  service: {
    id: 1,
    title: "Выездной шиномонтаж",
    slug: "shinomontazh"
  },
  options: [
    {
      id: 1,
      title: "Балансировка колеса",
      prices: [
        {
          id: 181,
          city_slug: "moskva",
          city_title: "Москва",
          technic_category_id: 1,
          technic_category_title: "Грузовой автомобиль",
          amount: "500.00"
        },
        {
          id: 182,
          city_slug: "moskva",
          city_title: "Москва",
          technic_category_id: 2,
          technic_category_title: "Легковой автомобиль",
          amount: "300.00"
        },
        {
          id: 183,
          city_slug: "moskva",
          city_title: "Москва",
          technic_category_id: 3,
          technic_category_title: "Кроссовер",
          amount: "350.00"
        }
      ]
    },
    // ... другие опции
  ],
  technicCategories: [
    { id: 1, title: "Грузовой автомобиль" },
    { id: 2, title: "Легковой автомобиль" },
    { id: 3, title: "Кроссовер" }
  ]
}
```

---

## 🔍 Фильтрация по категории техники

### Пример фильтрации на фронтенде

```javascript
// Фильтровать опции по выбранной категории техники
function filterOptionsByCategory(options, selectedCategoryId) {
  if (!selectedCategoryId) {
    // Если категория не выбрана, показать все опции со всеми ценами
    return options;
  }
  
  return options.map(option => {
    // Отфильтровать цены по выбранной категории
    const filteredPrices = option.prices.filter(
      price => price.technic_category_id === selectedCategoryId
    );
    
    return {
      ...option,
      prices: filteredPrices
    };
  }).filter(option => option.prices.length > 0); // Убрать опции без цен
}

// Использование
const filteredOptions = filterOptionsByCategory(
  pageData.options,
  selectedCategoryId
);
```

---

## 📊 Сортировка опций

Опции уже отсортированы по `display_order` и `title` в основном эндпоинте. Если нужна дополнительная сортировка:

```javascript
// Сортировка опций по названию
const sortedOptions = [...pageData.options].sort((a, b) => 
  a.title.localeCompare(b.title)
);

// Сортировка цен внутри опции по категории техники
const sortedPrices = option.prices.sort((a, b) => {
  // Сначала цены без категории, потом с категорией
  if (!a.technic_category_id && b.technic_category_id) return -1;
  if (a.technic_category_id && !b.technic_category_id) return 1;
  // Если обе имеют категорию, сортировать по названию категории
  if (a.technic_category_id && b.technic_category_id) {
    return a.technic_category_title.localeCompare(b.technic_category_title);
  }
  return 0;
});
```

---

## ⚡ Оптимизация запросов

### Вариант 1: Параллельная загрузка (рекомендуется)

```javascript
// Загрузить все данные параллельно
const [baseData, categoriesData] = await Promise.all([
  fetch(`/api/website/cities/${citySlug}/services/${serviceSlug}/`).then(r => r.json()),
  fetch(`/api/website/technic-categories/?service__slug=${serviceSlug}`).then(r => r.json())
]);

// Затем загрузить цены для всех опций параллельно
const optionsWithPrices = await Promise.all(
  baseData.options.map(option =>
    fetch(`/api/website/options/${option.id}/`)
      .then(r => r.json())
      .then(data => ({
        ...option,
        prices: data.prices.filter(p => p.city_slug === citySlug)
      }))
  )
);
```

### Вариант 2: Ленивая загрузка (для больших списков)

```javascript
// Загружать цены только при раскрытии аккордеона
async function loadOptionPrices(optionId, citySlug) {
  const response = await fetch(`/api/website/options/${optionId}/`);
  const data = await response.json();
  return data.prices.filter(p => p.city_slug === citySlug);
}

// В компоненте аккордеона
const [expandedOption, setExpandedOption] = useState(null);
const [optionPrices, setOptionPrices] = useState({});

const handleExpand = async (optionId) => {
  if (!optionPrices[optionId]) {
    const prices = await loadOptionPrices(optionId, citySlug);
    setOptionPrices({ ...optionPrices, [optionId]: prices });
  }
  setExpandedOption(optionId);
};
```

---

## 🎨 Пример структуры аккордеона

```jsx
function OptionsAccordion({ options, technicCategories, selectedCategory, onCategoryChange }) {
  const filteredOptions = filterOptionsByCategory(options, selectedCategory);
  
  return (
    <div>
      {/* Фильтр по категории техники */}
      <select value={selectedCategory} onChange={(e) => onCategoryChange(e.target.value)}>
        <option value="">Все категории</option>
        {technicCategories.map(cat => (
          <option key={cat.id} value={cat.id}>{cat.title}</option>
        ))}
      </select>
      
      {/* Аккордеон с опциями */}
      {filteredOptions.map(option => (
        <AccordionItem key={option.id} title={option.title}>
          <div>
            {option.prices.map(price => (
              <div key={price.id}>
                {price.technic_category_title && (
                  <span>{price.technic_category_title}: </span>
                )}
                <strong>{price.amount} руб.</strong>
              </div>
            ))}
          </div>
        </AccordionItem>
      ))}
    </div>
  );
}
```

---

## 📚 Связанные документы

- [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Краткий справочник API
- [API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md) - Страница услуги в городе
- [API_SERVICE_DETAIL.md](./API_SERVICE_DETAIL.md) - Детальная информация об услуге

---

## ✅ Итоговая схема запросов

```
1. GET /api/website/cities/{city_slug}/services/{service_slug}/
   → Получить базовую информацию и список опций

2. GET /api/website/technic-categories/?service__slug={service_slug}
   → Получить категории техники для фильтра

3. GET /api/website/options/{option_id}/ (для каждой опции)
   → Получить все цены опции
   → Отфильтровать по city_slug на фронтенде
```

**Итого:** 1 + 1 + N запросов (где N - количество опций)

---

**Дата создания:** 2025-01-02  
**Статус:** ✅ Актуально

