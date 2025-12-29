# 📚 Документация проекта 911 Corporate Website

## 🎯 Быстрый старт

### Для фронтенд-разработчиков

1. **[FRONTEND_QUICK_START.md](./FRONTEND_QUICK_START.md)** - Подключение к бекенду и первые запросы
2. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - Краткий справочник API эндпоинтов
3. **[API_FLOW_DIAGRAM.md](./API_FLOW_DIAGRAM.md)** - Визуальные схемы работы с API

### Для бекенд-разработчиков

1. **[BACKEND_TECHNICAL_SPECIFICATION.md](./BACKEND_TECHNICAL_SPECIFICATION.md)** - Техническая спецификация бекенда
2. **[TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md)** - Общая техническая спецификация проекта

---

## 📖 API Документация

### Основная документация

- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** 
  - ⭐ **Краткий справочник** по всем эндпоинтам
  - Быстрые примеры использования
  - Таблицы сравнения подходов

- **[911 Corporate Website API (1).yaml](./911%20Corporate%20Website%20API%20(1).yaml)**
  - 📄 **OpenAPI 3.0 спецификация**
  - Полное описание всех эндпоинтов
  - Схемы запросов и ответов
  - Можно открыть в Swagger UI

### Специализированные руководства

- **[API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md)**
  - 🎯 **Детальное руководство**: Страница услуги в городе
  - Примеры на JavaScript
  - Стратегии реализации (простая, lazy loading, предзагрузка)
  - Решение проблемы получения цен по категориям техники

- **[API_SERVICE_PAGE_SUMMARY.md](./API_SERVICE_PAGE_SUMMARY.md)**
  - 📊 **Итоговый отчет** по эндпоинтам страницы услуги
  - Сравнительная таблица подходов
  - Рекомендации по выбору стратегии

- **[API_FLOW_DIAGRAM.md](./API_FLOW_DIAGRAM.md)**
  - 🎨 **Визуальные схемы** flow работы с API
  - Диаграммы последовательности запросов
  - Сравнение вариантов реализации

### Инструменты и примеры

- **[API_EXAMPLES_SERVICE_PAGE.sh](./API_EXAMPLES_SERVICE_PAGE.sh)**
  - 🔧 **Bash скрипт** для тестирования API
  - Примеры curl запросов
  - Автоматическая проверка данных
  - Запуск: `bash docs/API_EXAMPLES_SERVICE_PAGE.sh`

---

## 🔍 Технические отчеты

### Исправления и обновления

- **[PAGINATION_FIX_REPORT.md](./PAGINATION_FIX_REPORT.md)**
  - 🐛 Исправление консистентности пагинации
  - Детали изменений в `OptionalLimitOffsetPagination`
  - Breaking changes для фронтенда

- **[ROOT_URL_FIX.md](./ROOT_URL_FIX.md)**
  - 🔧 Исправление 404 на root URL
  - Добавление JSON endpoint с информацией об API

- **[DOUBLE_SLASH_ISSUE.md](./DOUBLE_SLASH_ISSUE.md)**
  - 🔍 Расследование проблемы с двойным слешем
  - Рекомендации для фронтенда

### Анализ и проверки

- **[API_STATUS_REPORT.md](./API_STATUS_REPORT.md)**
  - ✅ Проверка статуса API и CORS
  - Диагностика подключения
  - Список активных эндпоинтов

- **[OPTION_PRICING_ANALYSIS.md](./OPTION_PRICING_ANALYSIS.md)**
  - 💰 **Анализ ценообразования опций**
  - Сравнение реализации в мобильном приложении и на сайте
  - Структура моделей `Option`, `OptionPrice`, `TechnicCategory`
  - Рекомендации по настройке цен

---

## 📐 Дизайн и концепция

- **[DESIGN_BRIEF.md](./DESIGN_BRIEF.md)**
  - 🎨 Дизайн-бриф проекта
  - Визуальная концепция
  - UI/UX требования

- **[APP_LANDING_DESIGN_CONCEPT.md](./APP_LANDING_DESIGN_CONCEPT.md)**
  - 📱 Концепция дизайна лендинга приложения
  - Структура страниц
  - Элементы интерфейса

---

## 💼 Бизнес-документация

- **[BUSINESS_DOCUMENTATION.md](./BUSINESS_DOCUMENTATION.md)**
  - 📋 Общая бизнес-документация
  - Описание бизнес-процессов
  - Требования заказчика

- **[BUSINESS_METRICS_ANALYSIS.md](./BUSINESS_METRICS_ANALYSIS.md)**
  - 📊 Анализ бизнес-метрик
  - KPI и показатели
  - Аналитика

- **[METRICS_TREE.md](./METRICS_TREE.md)**
  - 🌳 Дерево метрик проекта
  - Иерархия показателей
  - Связи между метриками

---

## 📚 Структура документации по темам

### 1. API и интеграция

```
API_QUICK_REFERENCE.md          ← Начни здесь (краткий справочник)
├── API_USAGE_SERVICE_PAGE.md   ← Детальное руководство
├── API_SERVICE_PAGE_SUMMARY.md ← Итоговый отчет
├── API_FLOW_DIAGRAM.md         ← Визуальные схемы
└── API_EXAMPLES_SERVICE_PAGE.sh ← Примеры и тесты
```

### 2. Техническая информация

```
BACKEND_TECHNICAL_SPECIFICATION.md  ← Спецификация бекенда
├── TECHNICAL_SPECIFICATION.md      ← Общая спецификация
├── OPTION_PRICING_ANALYSIS.md      ← Анализ ценообразования
└── 911 Corporate Website API (1).yaml ← OpenAPI схема
```

### 3. Решение проблем и обновления

```
PAGINATION_FIX_REPORT.md   ← Исправление пагинации
ROOT_URL_FIX.md            ← Исправление root URL
DOUBLE_SLASH_ISSUE.md      ← Проблема с double slash
API_STATUS_REPORT.md       ← Статус API и CORS
```

### 4. Для начинающих

```
FRONTEND_QUICK_START.md    ← Быстрый старт для фронтенда
API_QUICK_REFERENCE.md     ← Краткий справочник API
API_FLOW_DIAGRAM.md        ← Визуальные схемы
```

---

## 🎯 Популярные вопросы и ответы

### Q: Как получить список опций для страницы услуги в городе?

**A:** Используй основной эндпоинт:

```
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

Подробнее: [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) или [API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md)

---

### Q: Как получить все цены для опции (по всем категориям техники)?

**A:** Используй детальный эндпоинт опции:

```
GET /api/website/options/{option_id}/
```

Затем отфильтруй результат по `city_slug` на фронтенде.

Подробнее: [API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md#вариант-3-получить-все-цены-по-всем-категориям-техники)

---

### Q: Почему в списке опций только одна цена, хотя в базе их несколько?

**A:** Это ожидаемое поведение текущего API. Основной эндпоинт возвращает только первую найденную цену для города. Для получения всех цен используй детальный эндпоинт опции.

Подробнее: [API_SERVICE_PAGE_SUMMARY.md](./API_SERVICE_PAGE_SUMMARY.md#важное-ограничение)

---

### Q: Как работает пагинация API?

**A:** API использует limit/offset пагинацию и **всегда** возвращает объект с полями `count`, `next`, `previous`, `results`, даже если параметры не указаны.

Подробнее: [PAGINATION_FIX_REPORT.md](./PAGINATION_FIX_REPORT.md)

---

### Q: Как настроить цены для опций по городам?

**A:** Цены хранятся в модели `OptionPrice` и привязываются к городу и категории техники. Подробный анализ структуры данных см. в [OPTION_PRICING_ANALYSIS.md](./OPTION_PRICING_ANALYSIS.md)

---

### Q: Как проверить, что API работает корректно?

**A:** Используй bash скрипт:

```bash
bash docs/API_EXAMPLES_SERVICE_PAGE.sh
```

Или ручные curl команды из [API_STATUS_REPORT.md](./API_STATUS_REPORT.md)

---

### Q: Какие эндпоинты доступны?

**A:** Полный список см. в:
- [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - краткий справочник
- [911 Corporate Website API (1).yaml](./911%20Corporate%20Website%20API%20(1).yaml) - полная OpenAPI схема
- http://localhost:8000/ - JSON endpoint с активными эндпоинтами

---

## 🔄 История обновлений

### 2025-12-27

- ✅ Создана документация по API для страницы услуги в городе
  - `API_QUICK_REFERENCE.md` - краткий справочник
  - `API_USAGE_SERVICE_PAGE.md` - детальное руководство
  - `API_SERVICE_PAGE_SUMMARY.md` - итоговый отчет
  - `API_FLOW_DIAGRAM.md` - визуальные схемы
  - `API_EXAMPLES_SERVICE_PAGE.sh` - bash скрипт для тестирования

- ✅ Создан анализ ценообразования опций
  - `OPTION_PRICING_ANALYSIS.md` - сравнение с мобильным приложением

- ✅ Исправлена консистентность пагинации
  - `PAGINATION_FIX_REPORT.md` - отчет об исправлении
  - Все list эндпоинты теперь возвращают единый формат

- ✅ Исправлен root URL (404 → JSON)
  - `ROOT_URL_FIX.md` - документация изменения

- ✅ Исследована проблема с double slash
  - `DOUBLE_SLASH_ISSUE.md` - результаты расследования

- ✅ Проведена проверка API и CORS
  - `API_STATUS_REPORT.md` - отчет о проверке
  - `FRONTEND_QUICK_START.md` - гайд для фронтенда

---

## 📞 Контакты и поддержка

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/
- **API Root:** http://localhost:8000/

---

## 🚀 Следующие шаги

1. Ознакомиться с [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)
2. Изучить [API_USAGE_SERVICE_PAGE.md](./API_USAGE_SERVICE_PAGE.md) для конкретных задач
3. Протестировать API с помощью `API_EXAMPLES_SERVICE_PAGE.sh`
4. При необходимости обратиться к OpenAPI схеме: [911 Corporate Website API (1).yaml](./911%20Corporate%20Website%20API%20(1).yaml)

---

**Последнее обновление:** 2025-12-27  
**Статус документации:** ✅ Актуально

