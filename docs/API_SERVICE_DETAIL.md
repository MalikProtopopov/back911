# API - Детальная информация об услуге

## 📋 Обзор

Этот документ описывает API эндпоинты для получения детальной информации об услуге **без привязки к городу**.

Для страницы услуги в конкретном городе см. [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md).

---

## 🎯 Основной эндпоинт

### GET `/api/website/services/{service_slug}/`

**Описание:**  
Получить детальную информацию об услуге по её slug (без привязки к городу).

**Параметры:**
- `service_slug` (path, обязательный) - slug услуги (например: `shinomontazh`, `evakuator`)

**Примеры:**
```bash
GET /api/website/services/shinomontazh/
GET /api/website/services/evakuator/
GET /api/website/services/zapravka-toplivom/
```

---

## 📦 Структура ответа

```json
{
  "id": 1,
  "title": "Выездной шиномонтаж",
  "slug": "shinomontazh",
  "is_active": true,
  "display_order": 1,
  "content": {
    "meta_title": "Шиномонтаж - 911",
    "meta_description": "Описание услуги",
    "h1_title": "Выездной шиномонтаж",
    "description": "<p>HTML контент с описанием...</p>",
    "how_it_works_html": "<div>Как это работает...</div>",
    "benefits_html": "<div>Преимущества...</div>",
    "icon_url": "/static/icons/shinomontazh.svg",
    "cover_image_url": "/static/images/shinomontazh.jpg",
    "city_slug": null,
    "city_title": null,
    "updated_at": "2025-12-27T10:00:00+03:00"
  },
  "options_count": 56,
  "created_at": "2025-12-26T20:25:21.501618+03:00"
}
```

---

## 📊 Поля ответа

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | ID услуги |
| `title` | string | Название услуги |
| `slug` | string | URL-friendly идентификатор |
| `is_active` | boolean | Активна ли услуга |
| `display_order` | integer | Порядок отображения |
| `content` | object\|null | HTML контент услуги (общий, без привязки к городу) |
| `options_count` | integer | Количество активных опций для услуги |
| `created_at` | datetime | Дата создания |

---

### Поля объекта `content`

| Поле | Тип | Описание |
|------|-----|----------|
| `meta_title` | string\|null | Meta title для SEO |
| `meta_description` | string\|null | Meta description для SEO |
| `h1_title` | string\|null | H1 заголовок страницы |
| `description` | string\|null | HTML описание услуги |
| `how_it_works_html` | string\|null | HTML блок "Как это работает" |
| `benefits_html` | string\|null | HTML блок "Преимущества" |
| `icon_url` | string\|null | URL иконки услуги |
| `cover_image_url` | string\|null | URL обложки услуги |
| `city_slug` | string\|null | Всегда `null` для общего контента |
| `city_title` | string\|null | Всегда `null` для общего контента |
| `updated_at` | datetime | Дата последнего обновления |

**Важно:**  
- Если контент не настроен, поле `content` будет `null`
- Возвращается **только общий контент** (без привязки к городу)
- Для контента, специфичного для города, используй эндпоинт `/api/website/cities/{city_slug}/services/{service_slug}/`

---

## 🔗 Дополнительные эндпоинты

### GET `/api/website/services/{service_slug}/options/`

**Описание:**  
Получить список опций для конкретной услуги.

**Параметры:**
- `service_slug` (path, обязательный) - slug услуги

**Пример:**
```bash
GET /api/website/services/shinomontazh/options/
```

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Зарядка аккумулятора",
    "service_id": 1,
    "service_title": "Выездной шиномонтаж",
    "service_slug": "shinomontazh",
    "is_active": true
  },
  {
    "id": 2,
    "title": "Балансировка колеса",
    "service_id": 1,
    "service_title": "Выездной шиномонтаж",
    "service_slug": "shinomontazh",
    "is_active": true
  }
  // ... остальные опции
]
```

**Важно:**
- Возвращает **только активные опции** (is_active=True)
- Возвращает **базовую информацию** об опциях (без цен)
- Для получения цен используй эндпоинт `/api/website/options/{option_id}/` или `/api/website/cities/{city_slug}/services/{service_slug}/`

---

## 🚀 Примеры использования

### JavaScript (Fetch API)

```javascript
// Получить детальную информацию об услуге
async function getServiceDetail(serviceSlug) {
  const response = await fetch(
    `/api/website/services/${serviceSlug}/`
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const service = await response.json();
  
  return {
    id: service.id,
    title: service.title,
    slug: service.slug,
    content: service.content, // HTML контент или null
    optionsCount: service.options_count,
  };
}

// Использование
const service = await getServiceDetail('shinomontazh');
console.log('Услуга:', service.title);
console.log('Опций:', service.optionsCount);
console.log('Контент:', service.content?.description);
```

---

### Получить опции услуги

```javascript
// Получить список опций для услуги
async function getServiceOptions(serviceSlug) {
  const response = await fetch(
    `/api/website/services/${serviceSlug}/options/`
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const options = await response.json();
  return options;
}

// Использование
const options = await getServiceOptions('shinomontazh');
console.log(`Найдено опций: ${options.length}`);
options.forEach(option => {
  console.log(`- ${option.title}`);
});
```

---

### Комбинированный пример

```javascript
// Получить полную информацию об услуге с опциями
async function getFullServiceInfo(serviceSlug) {
  // 1. Получить детальную информацию
  const serviceResponse = await fetch(
    `/api/website/services/${serviceSlug}/`
  );
  const service = await serviceResponse.json();
  
  // 2. Получить опции
  const optionsResponse = await fetch(
    `/api/website/services/${serviceSlug}/options/`
  );
  const options = await optionsResponse.json();
  
  return {
    ...service,
    options: options,
  };
}

// Использование
const fullInfo = await getFullServiceInfo('shinomontazh');
console.log('Услуга:', fullInfo.title);
console.log('Опций:', fullInfo.options.length);
console.log('Контент:', fullInfo.content?.description);
```

---

## ⚠️ Важные замечания

### 1. Контент без города

Эндпоинт `/api/website/services/{slug}/` возвращает **только общий контент** услуги (без привязки к городу).

Если нужен контент, специфичный для города:
- Используй `/api/website/cities/{city_slug}/services/{service_slug}/`
- Он вернет контент, специфичный для города, или общий контент, если специфичного нет

---

### 2. Опции без цен

Эндпоинт `/api/website/services/{slug}/options/` возвращает **только базовую информацию** об опциях (без цен).

Для получения цен:
- **С ценами для конкретного города:** `/api/website/cities/{city_slug}/services/{service_slug}/`
- **Все цены опции:** `/api/website/options/{option_id}/`

---

### 3. SEO метаданные

Эндпоинт `/api/website/services/{slug}/` **не возвращает SEO метаданные**.

Для получения SEO:
- Используй `/api/website/seo-meta/by-slug/?slug=/shinomontazh/`
- Или `/api/website/cities/{city_slug}/services/{service_slug}/` (включает SEO)

---

## 🔄 Сравнение с эндпоинтом "услуга в городе"

| Характеристика | `/services/{slug}/` | `/cities/{city}/services/{service}/` |
|----------------|---------------------|--------------------------------------|
| **Город** | ❌ Нет | ✅ Есть |
| **Услуга** | ✅ Есть | ✅ Есть |
| **Контент** | Общий | Город + общий (приоритет городу) |
| **Опции** | Базовые (без цен) | С ценами для города |
| **SEO** | ❌ Нет | ✅ Есть |
| **Использование** | Общая страница услуги | Страница услуги в городе |

---

## 📚 Связанные документы

- [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Краткий справочник API
- [API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md) - Страница услуги в городе
- [API_SERVICE_PAGE_SUMMARY.md](./API_SERVICE_PAGE_SUMMARY.md) - Итоговый отчет

---

## ✅ Тестирование

### cURL примеры

```bash
# Получить детальную информацию об услуге
curl -X GET "http://localhost:8000/api/website/services/shinomontazh/"

# Получить список опций услуги
curl -X GET "http://localhost:8000/api/website/services/shinomontazh/options/"

# С форматированием JSON
curl -X GET "http://localhost:8000/api/website/services/shinomontazh/" | python3 -m json.tool
```

---

**Дата создания:** 2025-12-27  
**Статус:** ✅ Актуально


