# Итоговый отчет: API для страницы услуги в городе

**Дата:** 2025-12-27  
**Автор:** AI Assistant  
**Тема:** Какие API запросы использовать для страницы услуги в выбранном городе

---

## 📋 Задача

Определить правильные API запросы для получения списка опций с ценами для конкретной услуги в конкретном городе.

---

## ✅ Решение

### Основной рекомендованный эндпоинт

```
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

**Примеры:**
- `GET /api/website/cities/moskva/services/shinomontazh/`
- `GET /api/website/cities/sankt-peterburg/services/evakuator/`

**Что возвращает:**
```json
{
  "city": { /* данные города */ },
  "service": { /* данные услуги */ },
  "options": [
    {
      "id": 1,
      "title": "Балансировка колеса",
      "price": {
        "amount": "500.00",
        "technic_category": "Грузовой автомобиль"
      }
    }
  ],
  "content": { /* HTML контент */ },
  "seo": { /* SEO метаданные */ }
}
```

**Преимущества:**
- ✅ Один запрос получает ВСЁ для страницы
- ✅ Оптимизирован для производительности
- ✅ Включает город, услугу, опции, контент и SEO
- ✅ Фильтрует опции — показывает только те, у которых есть цена в данном городе

---

## ⚠️ Важное ограничение

**Текущее поведение:** Каждая опция возвращает только **одну цену** (первую найденную для города).

Если у опции есть разные цены для разных категорий техники (легковой, кроссовер, внедорожник), вернётся только одна цена.

### Пример проблемы

В базе данных:
```
Опция "Балансировка колеса" в Москве:
- Грузовой: 500 руб.
- Легковой: 300 руб.
- Кроссовер: 350 руб.
```

API возвращает:
```json
{
  "title": "Балансировка колеса",
  "price": {
    "amount": "500.00",
    "technic_category": "Грузовой автомобиль"  // Только одна!
  }
}
```

---

## 🔧 Решение для получения всех цен

Если нужны **ВСЕ цены** по всем категориям техники:

```
GET /api/website/options/{option_id}/
```

**Пример:**
```
GET /api/website/options/1/
```

**Возвращает:**
```json
{
  "id": 1,
  "title": "Балансировка колеса",
  "prices": [
    {
      "city_slug": "moskva",
      "technic_category_title": "Грузовой автомобиль",
      "amount": "500.00"
    },
    {
      "city_slug": "moskva",
      "technic_category_title": "Легковой автомобиль",
      "amount": "300.00"
    },
    {
      "city_slug": "moskva",
      "technic_category_title": "Кроссовер",
      "amount": "350.00"
    }
    // + цены для других городов
  ]
}
```

**На фронтенде фильтруем:**
```javascript
const moscowPrices = data.prices.filter(p => p.city_slug === 'moskva');
```

---

## 📊 Дополнительные полезные эндпоинты

### 1. Категории техники для услуги

```
GET /api/website/technic-categories/?service__slug={service_slug}
```

**Пример:**
```
GET /api/website/technic-categories/?service__slug=shinomontazh
```

**Возвращает:**
```json
{
  "count": 2,
  "results": [
    {"id": 1, "title": "Грузовой автомобиль"},
    {"id": 3, "title": "Легковой автомобиль"}
  ]
}
```

**Использование:** Показать фильтр по категориям техники на фронтенде.

---

### 2. Опции по городу (альтернатива)

```
GET /api/website/options/by-city/?city={city_slug}&service={service_slug}
```

**Пример:**
```
GET /api/website/options/by-city/?city=moskva&service=shinomontazh
```

**Возвращает:** Массив опций (без данных города, услуги, контента, SEO)

**Когда использовать:**
- Если нужны только опции, без остальных данных страницы
- ⚠️ Тоже возвращает только одну цену на опцию

---

## 🚀 Рекомендуемая стратегия реализации

### Вариант 1: Простое отображение (одна цена на опцию)

```javascript
// 1. Загрузить всю страницу
const response = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const page = await response.json();

// 2. Отобразить данные
console.log('Город:', page.city.title);
console.log('Услуга:', page.service.title);
console.log('Опций:', page.options.length);

// 3. Показать опции с ценами
page.options.forEach(option => {
  console.log(`${option.title}: ${option.price.amount} руб.`);
});
```

**Плюсы:** Простота, один запрос  
**Минусы:** Не показывает все цены по категориям

---

### Вариант 2: Отображение цен по категориям техники

#### A. Lazy loading (рекомендуется)

```javascript
// 1. Загрузить основную страницу
const mainResponse = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const page = await mainResponse.json();

// 2. Показать страницу с базовыми ценами
renderPage(page);

// 3. Когда пользователь кликает на опцию - загрузить детали
async function onOptionClick(optionId, citySlug) {
  const response = await fetch(`/api/website/options/${optionId}/`);
  const data = await response.json();
  
  // Отфильтровать цены для города
  const cityPrices = data.prices.filter(p => p.city_slug === citySlug);
  
  // Показать все цены по категориям
  showPriceModal(cityPrices);
}
```

**Плюсы:** Быстрая загрузка страницы, детали по требованию  
**Минусы:** Дополнительные запросы при клике

---

#### B. Предзагрузка всех цен

```javascript
// 1. Загрузить основную страницу
const mainResponse = await fetch(
  `/api/website/cities/moskva/services/shinomontazh/`
);
const page = await mainResponse.json();

// 2. Для каждой опции загрузить все цены
const optionsWithAllPrices = await Promise.all(
  page.options.map(async (option) => {
    const response = await fetch(`/api/website/options/${option.id}/`);
    const data = await response.json();
    
    // Фильтровать только цены для Москвы
    const cityPrices = data.prices.filter(
      p => p.city_slug === 'moskva'
    );
    
    return {
      ...option,
      allPrices: cityPrices
    };
  })
);

// 3. Показать опции с возможностью выбора категории
renderOptionsWithCategories(optionsWithAllPrices);
```

**Плюсы:** Все данные доступны сразу, нет задержек при взаимодействии  
**Минусы:** Много запросов (N+1), медленная загрузка

---

## 💡 Улучшение API (опционально)

Если хочешь, чтобы основной эндпоинт возвращал **все цены** для каждой опции, нужно изменить сериализатор:

### Текущий код (website_api/serializers/option.py):

```python
def get_price(self, obj):
    """Get price for the city from context"""
    city = self.context.get('city')
    price_query = obj.prices.filter(city=city)
    price = price_query.first()  # ⚠️ Берет только первую
    
    if price:
        return {
            'amount': str(price.amount),
            'technic_category': price.technic_category.title if price.technic_category else None
        }
    return None
```

### Предлагаемое изменение:

```python
def get_prices(self, obj):  # Изменено: price -> prices
    """Get ALL prices for the city from context"""
    city = self.context.get('city')
    
    if not city:
        return []
    
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

**Результат:**

```json
{
  "id": 1,
  "title": "Балансировка колеса",
  "prices": [  // Теперь массив!
    {"amount": "500.00", "technic_category_id": 1, "technic_category": "Грузовой"},
    {"amount": "300.00", "technic_category_id": 2, "technic_category": "Легковой"},
    {"amount": "350.00", "technic_category_id": 3, "technic_category": "Кроссовер"}
  ]
}
```

**Преимущества:**
- ✅ Один запрос получает все необходимые данные
- ✅ Нет проблемы N+1
- ✅ Фронтенд может сам выбирать, какие цены показывать

**Недостатки:**
- ⚠️ Breaking change для фронтенда (`price` -> `prices`)
- ⚠️ Немного больший размер ответа

---

## 📈 Тестирование

### Проверка основного эндпоинта

```bash
curl -s "http://localhost:8000/api/website/cities/moskva/services/shinomontazh/" | \
  python3 -c "import sys, json; d = json.load(sys.stdin); \
  print('Город:', d['city']['title']); \
  print('Услуга:', d['service']['title']); \
  print('Опций:', len(d['options'])); \
  print('Контент:', d['content'] is not None); \
  print('SEO:', d['seo'] is not None)"
```

**Результат:**
```
Город: Москва
Услуга: Выездной шиномонтаж
Опций: 45
Контент: True
SEO: True
```

### Проверка категорий техники

```bash
curl -s "http://localhost:8000/api/website/technic-categories/?service__slug=shinomontazh"
```

**Результат:**
```json
{
  "count": 2,
  "results": [
    {"id": 1, "title": "Грузовой автомобиль"},
    {"id": 3, "title": "Легковой автомобиль"}
  ]
}
```

---

## 📝 Итоговая таблица сравнения

| Подход | Запросов | Данных | Сложность | Рекомендация |
|--------|----------|--------|-----------|--------------|
| Основной эндпоинт | 1 | Минимум | Низкая | ⭐⭐⭐ Для простых страниц |
| Основной + lazy load | 1 + N | Средне | Средняя | ⭐⭐ Для интерактивности |
| Основной + предзагрузка | 1 + N | Много | Высокая | ⭐ Если нужны все цены |
| Новый сериализатор (изменение API) | 1 | Средне | Низкая | ⭐⭐⭐ Оптимально (требует изменений) |

---

## 🎯 Финальные рекомендации

### Для текущей реализации (без изменений бекенда):

1. **Используй основной эндпоинт** для базовой загрузки:
   ```
   GET /api/website/cities/{city_slug}/services/{service_slug}/
   ```

2. **Если нужны цены по категориям**, используй lazy loading:
   - При клике на опцию делай запрос: `GET /api/website/options/{option_id}/`
   - Фильтруй цены по `city_slug` на фронтенде

3. **Получи категории техники** для отображения фильтров:
   ```
   GET /api/website/technic-categories/?service__slug={service_slug}
   ```

### Для улучшения (требует изменений бекенда):

Измени `OptionWithCityPriceSerializer`, чтобы поле `price` стало `prices` (массивом). Это позволит получить все цены в одном запросе.

---

## 📚 Созданная документация

1. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - Краткий справочник API
2. **[API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md)** - Детальное руководство с примерами
3. **[API_EXAMPLES_SERVICE_PAGE.sh](./API_EXAMPLES_SERVICE_PAGE.sh)** - Bash скрипт для тестирования
4. **[OPTION_PRICING_ANALYSIS.md](./OPTION_PRICING_ANALYSIS.md)** - Анализ ценообразования

---

## ✅ Заключение

Для страницы услуги в городе **правильный запрос**:

```
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

Этот эндпоинт возвращает:
- ✅ Информацию о городе и услуге
- ✅ Опции с ценами (одна цена на опцию)
- ✅ HTML контент страницы
- ✅ SEO метаданные

**Если нужны все цены по категориям техники** — используй дополнительный запрос:
```
GET /api/website/options/{option_id}/
```

и фильтруй результат по `city_slug` на фронтенде.

---

**Дата создания:** 2025-12-27  
**Статус:** ✅ Актуально  
**Следующий шаг:** Согласовать с фронтенд-разработчиком стратегию отображения цен

