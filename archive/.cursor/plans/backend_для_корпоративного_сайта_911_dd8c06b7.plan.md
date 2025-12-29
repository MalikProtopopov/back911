---
name: Backend для корпоративного сайта 911
overview: Создание полноценного Django REST API backend для корпоративного сайта с отдельной БД, автоматической синхронизацией данных из основного приложения, всеми необходимыми endpoints (города, услуги, метрики, контакты, заявки, SEO), и фоновыми задачами через Celery.
todos:
  - id: setup-project
    content: Инициализация Django проекта и установка зависимостей
    status: pending
  - id: create-models
    content: Создание моделей для 9 таблиц и применение миграций
    status: pending
    dependencies:
      - setup-project
  - id: create-serializers
    content: Создание serializers для всех моделей
    status: pending
    dependencies:
      - create-models
  - id: create-viewsets
    content: Создание ViewSets для API endpoints с фильтрацией
    status: pending
    dependencies:
      - create-serializers
  - id: setup-urls
    content: Настройка URL routing и подключение API
    status: pending
    dependencies:
      - create-viewsets
  - id: create-celery-tasks
    content: Создание Celery задач для синхронизации и метрик
    status: pending
    dependencies:
      - create-models
  - id: setup-admin
    content: Настройка Django Admin для управления контентом
    status: pending
    dependencies:
      - create-models
  - id: setup-caching
    content: Настройка Redis кеширования для API
    status: pending
    dependencies:
      - create-viewsets
  - id: create-fixtures
    content: Создание fixtures с начальными данными
    status: pending
    dependencies:
      - create-models
  - id: write-tests
    content: Написание тестов для models, API и tasks
    status: pending
    dependencies:
      - create-viewsets
      - create-celery-tasks
  - id: setup-documentation
    content: Настройка API документации (Swagger)
    status: pending
    dependencies:
      - setup-urls
  - id: optimize-queries
    content: Оптимизация SQL запросов и добавление индексов
    status: pending
    dependencies:
      - write-tests
  - id: create-readme
    content: Создание README с инструкциями по запуску
    status: pending
    dependencies:
      - setup-project
---

# Backend для корпоративного сайта 911

## Архитектура решения

Создаем **отдельный Django проект** в `/Users/mak/Desktop/911_backend_website/` с собственной БД, которая будет синхронизироваться с основным приложением через Celery.

**Ключевые преимущества:**

- Независимое развертывание и масштабирование
- Отдельная БД оптимизирована для чтения (read-heavy workload)
- Не влияет на производительность основного приложения
- Простота управления кешем и индексами

## Структура проекта

```
911_backend_website/
├── website_project/          # Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── website_api/              # Django app
│   ├── models/
│   ├── serializers/
│   ├── views/
│   ├── tasks/
│   ├── admin/
│   └── tests/
├── manage.py
├── requirements.txt
└── README.md
```

## Этап 1: Инициализация проекта

### 1.1 Создание Django проекта

Создадим новый Django проект с правильной структурой:

```bash
cd /Users/mak/Desktop/911_backend_website/
django-admin startproject website_project .
python manage.py startapp website_api
```

### 1.2 Установка зависимостей

[`requirements.txt`](requirements.txt) будет содержать:

- Django 5.0.3
- djangorestframework
- django-filter
- django-cors-headers
- psycopg2-binary
- redis
- celery
- python-slugify
- pillow
- drf-spectacular (для документации API)

### 1.3 Настройка settings.py

В [`website_project/settings.py`](website_project/settings.py):

- Настроим подключение к PostgreSQL (отдельная БД: `website_911_db`)
- Добавим INSTALLED_APPS: `rest_framework`, `django_filters`, `corsheaders`, `drf_spectacular`, `website_api`
- Настроим Redis для кеша
- Настроим CORS для frontend
- Добавим настройки для DRF (пагинация, фильтрация)

### 1.4 Настройка Celery

Создадим [`website_project/celery.py`](website_project/celery.py) для фоновых задач:

- Синхронизация данных из основной БД
- Обновление метрик
- Обновление кеша
- Обработка заявок

## Этап 2: Модели базы данных

Создадим 9 новых моделей в [`website_api/models/`](website_api/models/):

### 2.1 Основные таблицы для контента

**City** - города (копия из основной БД)

```python
class City(models.Model):
    title = CharField(max_length=255)
    is_active = BooleanField(default=True)
```

**Service** - услуги (копия из основной БД)

```python
class Service(models.Model):
    title = CharField(max_length=255)
    is_active = BooleanField(default=True)
```

**WebsiteCityContent** - контент страниц городов

- Поля: city (FK), slug, title, meta_description, h1_title, short_description, full_description (HTML), partner_count (cache), avg_rating (cache), review_count (cache)
- Автоматически создается при синхронизации городов

**WebsiteServiceContent** - контент страниц услуг

- Поля: service (FK), city (FK nullable), slug, title, description (HTML), how_it_works_html, benefits_html, icon_url, cover_image_url
- city=NULL означает общее описание услуги

### 2.2 Таблицы для опций и цен

**Option** - опции услуг (копия из основной БД)

**OptionPrice** - цены опций по городам

- Поля: option (FK), city (FK), technic_category (FK nullable), amount (Decimal)
- Синхронизируется из основной БД

**TechnicCategory** - категории техники (копия)

### 2.3 Дополнительные таблицы

**WebsiteAdvantage** - преимущества платформы

- Поля: target_audience ('client', 'partner', 'both'), title, description, icon_name, display_order

**WebsiteMetric** - метрики для сайта

- Поля: metric_key (unique), value, display_label, description, metric_type, is_visible_on_site, is_auto_calculated
- Примеры: total_cities, total_partners, avg_rating, etc.

**WebsiteContact** - контакты

- Поля: contact_type ('phone', 'email', 'telegram', etc.), value, label, is_app_store_link, platform, icon_name

**WebsiteAppLink** - ссылки на приложения

- Поля: platform ('ios', 'android'), app_type ('client', 'partner'), store_url, qr_code_url, version

**WebsiteSeoMeta** - SEO метаданные

- Поля: page_type, city (FK nullable), service (FK nullable), title, meta_description, meta_keywords, h1_title, full_slug (unique), og_title, og_description, schema_json (JSONB)

**WebsiteLead** - заявки с сайта

- Поля: name, phone, email, city (FK), service (FK), message, source_page, utm_source, utm_medium, status ('new', 'processing', 'converted'), is_synced_to_main_app

**Review** - отзывы (копия из основной БД)

- Для отображения на сайте

### 2.4 Создание миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

## Этап 3: Celery задачи для синхронизации

Создадим задачи в [`website_api/tasks/`](website_api/tasks/):

### 3.1 Синхронизация из основной БД

**sync_cities.py** - синхронизация городов

- Подключается к основной БД (911-develop)
- Копирует данные из `city_db`
- Создает/обновляет записи в локальной БД
- Автоматически создает `WebsiteCityContent` для новых городов

**sync_services.py** - синхронизация услуг и опций

- Копирует `service_db`, `option_db`, `option_price_db`, `technic_category_db`

**sync_reviews.py** - синхронизация отзывов

- Копирует последние отзывы для отображения на сайте

### 3.2 Обновление метрик

**update_metrics.py** - автоматический расчет метрик

- Подключается к основной БД для получения актуальных данных
- Обновляет записи в `WebsiteMetric`:
  - total_cities, total_partners, active_partners
  - avg_review_rating, total_reviews, positive_review_percent
  - Метрики по городам (partner_count, avg_rating)

### 3.3 Обновление кеша

**update_city_cache.py** - обновление кешированных данных

- Обновляет `partner_count`, `avg_rating`, `review_count` в `WebsiteCityContent`
- Инвалидирует Redis кеш для API

### 3.4 Обработка заявок

**process_lead.py** - обработка заявок

- Отправка уведомлений администратору
- Интеграция с основным приложением (создание заказа в основной БД)
- Опционально: отправка в CRM

### 3.5 Настройка периодических задач (Celery Beat)

```python
# website_project/celery.py
app.conf.beat_schedule = {
    'sync-cities-every-hour': {
        'task': 'website_api.tasks.sync_cities',
        'schedule': crontab(minute=0),  # Каждый час
    },
    'sync-services-every-hour': {
        'task': 'website_api.tasks.sync_services',
        'schedule': crontab(minute=10),
    },
    'update-metrics-every-15min': {
        'task': 'website_api.tasks.update_metrics',
        'schedule': crontab(minute='*/15'),
    },
    'update-city-cache-daily': {
        'task': 'website_api.tasks.update_city_cache',
        'schedule': crontab(hour=2, minute=0),  # 2:00 ночи
    },
    'sync-reviews-every-30min': {
        'task': 'website_api.tasks.sync_reviews',
        'schedule': crontab(minute='*/30'),
    },
}
```

## Этап 4: Serializers

Создадим serializers в [`website_api/serializers/`](website_api/serializers/):

### 4.1 City Serializers

**CityListSerializer** - для списка городов

- Поля: id, title, slug, partner_count, avg_rating, short_description

**CityDetailSerializer** - для детальной страницы

- Включает: SEO данные, полный контент, статистику, список услуг, рабочие зоны

### 4.2 Service Serializers

**ServiceListSerializer** - список услуг

**ServiceDetailSerializer** - детальная информация об услуге

- С опциональной фильтрацией по городу

**CityServiceSerializer** - комбинированная страница город+услуга

### 4.3 Option Serializers

**OptionPriceSerializer** - цены опций с группировкой по категориям техники

### 4.4 Прочие Serializers

- **AdvantageSerializer**
- **MetricSerializer**
- **ContactSerializer**
- **AppLinkSerializer**
- **SeoMetaSerializer**
- **LeadSerializer** (с валидацией телефона)
- **ReviewSerializer**

## Этап 5: Views и ViewSets

Создадим ViewSets в [`website_api/views/`](website_api/views/):

### 5.1 City Views

**CityViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/cities/` - список городов
  - Фильтры: is_active, has_partners, has_services
  - Поиск: по названию
  - Сортировка: name, -partner_count, display_order
  - Кеш: 15 минут

- `GET /api/website/cities/{slug}/` - детальная страница города
  - Кеш: 30 минут

### 5.2 Service Views

**ServiceViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/services/` - список услуг
  - Фильтры: city_id, city_slug, is_active

- `GET /api/website/services/{slug}/` - детальная страница услуги
  - Query param: city_id или city_slug для контекста

**CityServiceView** (APIView)

- `GET /api/website/cities/{city_slug}/services/{service_slug}/` - комбинированная страница

### 5.3 Option Views

**OptionViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/options/` - список опций с ценами
  - Фильтры: service_id, city_id, technic_category_id

### 5.4 Advantage Views

**AdvantageViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/advantages/` - преимущества
  - Фильтры: target_audience, is_active

### 5.5 Metric Views

**MetricViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/metrics/` - метрики
  - Фильтры: metric_type, is_visible, city_id

### 5.6 Contact Views

**ContactViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/contacts/` - контакты
  - Фильтры: contact_type, is_app_link

**AppLinkViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/app-links/` - ссылки на приложения
  - Фильтры: platform, app_type

### 5.7 Lead Views

**LeadViewSet** (CreateModelMixin, GenericViewSet)

- `POST /api/website/leads/` - создание заявки
  - Валидация телефона, email
  - Запуск Celery задачи для обработки
  - Rate limiting: 5 заявок в час с одного IP

### 5.8 SEO Views

**SeoMetaViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/seo-meta/` - SEO метаданные
  - Параметры: page_type, city_slug, service_slug, full_slug

### 5.9 Review Views

**ReviewViewSet** (ReadOnlyModelViewSet)

- `GET /api/website/reviews/` - отзывы
  - Фильтры: city_id, service_id, partner_id, rating, has_comment
  - Пагинация: 10 на страницу

## Этап 6: URL Routing

Создадим [`website_api/urls.py`](website_api/urls.py) с использованием DefaultRouter:

```python
router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'options', OptionViewSet, basename='option')
router.register(r'advantages', AdvantageViewSet, basename='advantage')
router.register(r'metrics', MetricViewSet, basename='metric')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'app-links', AppLinkViewSet, basename='app-link')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'seo-meta', SeoMetaViewSet, basename='seo-meta')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('cities/<slug:city_slug>/services/<slug:service_slug>/', CityServiceView.as_view()),
]
```

Обновим [`website_project/urls.py`](website_project/urls.py):

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/website/', include('website_api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
]
```

## Этап 7: Django Admin

Создадим удобную админ-панель в [`website_api/admin/`](website_api/admin/):

### 7.1 City Admin

- Фильтры: is_active, has_partners
- Поиск: по названию
- Inline редактирование: WebsiteCityContent
- Кнопка "Обновить кеш" для ручного обновления

### 7.2 Service Admin

- Inline редактирование: WebsiteServiceContent
- Отображение количества опций

### 7.3 Lead Admin

- Фильтры: status, city, service, created_at
- Список: показать имя, телефон, город, услугу, статус
- Actions: "Отметить как обработано", "Экспорт в CSV"
- Автоматическая смена статуса при обработке

### 7.4 Metric Admin

- Группировка по metric_type
- Кнопка "Пересчитать метрики" для ручного запуска

### 7.5 Прочие Admin

- **AdvantageAdmin**: сортировка drag-and-drop
- **ContactAdmin**: группировка по типу
- **SeoMetaAdmin**: предпросмотр полного slug

## Этап 8: Кеширование

Настроим Redis кеширование для оптимизации:

### 8.1 Кеш для ViewSets

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class CityViewSet(ReadOnlyModelViewSet):
    @method_decorator(cache_page(60 * 15))  # 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 30))  # 30 минут
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

### 8.2 Инвалидация кеша

При обновлении данных через Celery задачи:

```python
from django.core.cache import cache

def invalidate_city_cache(city_id):
    cache.delete(f'city_detail_{city_id}')
    cache.delete('city_list')
```

## Этап 9: Fixtures - Начальные данные

Создадим [`website_api/fixtures/initial_data.json`](website_api/fixtures/initial_data.json):

### 9.1 Преимущества (6 штук)

- Для клиентов: "Быстрый отклик", "Прозрачное ценообразование", "Рейтинг и отзывы"
- Для партнеров: "Стабильный поток заказов", "Низкая комиссия"
- Для обоих: "Работа 24/7"

### 9.2 Метрики (6 штук)

- total_cities: "82 города"
- total_partners: "195 партнеров"
- active_partners: "155 активных"
- avg_review_rating: "4.84/5"
- total_reviews: "2728 отзывов"
- positive_reviews_percent: "92%"

### 9.3 Контакты (5 штук)

- Телефон горячей линии
- WhatsApp
- Telegram
- Email
- VK/Instagram

### 9.4 Ссылки на приложения (4 штуки)

- iOS Client
- Android Client
- iOS Partner
- Android Partner

Загрузка:

```bash
python manage.py loaddata website_api/fixtures/initial_data.json
```

## Этап 10: Тестирование

Создадим тесты в [`website_api/tests/`](website_api/tests/):

### 10.1 Тесты моделей

- Проверка создания записей
- Проверка уникальности slug'ов
- Проверка валидации полей

### 10.2 Тесты API

- Тест списка городов (фильтрация, поиск, сортировка)
- Тест детальной страницы города
- Тест списка услуг с фильтрацией по городу
- Тест комбинированной страницы город+услуга
- Тест создания заявки (валидация, rate limiting)
- Тест получения метрик
- Тест получения SEO метаданных

### 10.3 Тесты Celery задач

- Тест синхронизации городов
- Тест обновления метрик
- Тест обработки заявки

Запуск:

```bash
python manage.py test website_api
```

## Этап 11: API Документация

Используем drf-spectacular для автоматической документации:

### 11.1 Настройка

В [`website_project/settings.py`](website_project/settings.py):

```python
SPECTACULAR_SETTINGS = {
    'TITLE': '911 Corporate Website API',
    'DESCRIPTION': 'REST API для корпоративного сайта 911',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

### 11.2 Добавление описаний

Используем декораторы `@extend_schema` для кастомизации документации ViewSets.

### 11.3 Доступ к документации

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema (JSON): `http://localhost:8000/api/schema/`

## Этап 12: Оптимизация

### 12.1 Оптимизация SQL запросов

Используем `select_related` и `prefetch_related`:

```python
queryset = WebsiteCityContent.objects.select_related('city').prefetch_related(
    'city__services',
    'city__working_zones'
)
```

### 12.2 Добавление индексов

В моделях:

```python
class Meta:
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['is_active', 'display_order']),
    ]
```

### 12.3 CORS настройки

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend dev
    "https://911service.ru",  # Production
]
```

### 12.4 Rate Limiting

Используем django-ratelimit для защиты endpoint'а заявок:

```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/h', method='POST')
def create(self, request, *args, **kwargs):
    return super().create(request, *args, **kwargs)
```

## Этап 13: README и документация

Создадим [`README.md`](README.md) с инструкциями:

### 13.1 Установка и запуск

```bash
# Клонирование и установка
cd /Users/mak/Desktop/911_backend_website/
pip install -r requirements.txt

# Настройка БД
createdb website_911_db
python manage.py migrate

# Загрузка начальных данных
python manage.py loaddata website_api/fixtures/initial_data.json

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver

# Запуск Celery
celery -A website_project worker -l info
celery -A website_project beat -l info
```

### 13.2 Первая синхронизация

```python
# В Django shell
python manage.py shell

from website_api.tasks import sync_cities, sync_services, update_metrics

sync_cities.delay()
sync_services.delay()
update_metrics.delay()
```

### 13.3 Переменные окружения

Создадим [`.env.example`](.env.example):

```
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Main App Database (для синхронизации)
MAIN_DB_NAME=911_db
MAIN_DB_USER=postgres
MAIN_DB_PASSWORD=password
MAIN_DB_HOST=localhost
MAIN_DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
```

## Итоговый чеклист

**Инфраструктура:**

- ✅ Создать Django проект
- ✅ Настроить PostgreSQL (отдельная БД)
- ✅ Настроить Redis
- ✅ Настроить Celery + Beat

**Модели и миграции:**

- ✅ Создать 9 моделей
- ✅ Применить миграции
- ✅ Создать fixtures

**Celery задачи:**

- ✅ Синхронизация городов
- ✅ Синхронизация услуг/опций
- ✅ Синхронизация отзывов
- ✅ Обновление метрик
- ✅ Обработка заявок

**API:**

- ✅ Создать 13+ serializers
- ✅ Создать 10 ViewSets
- ✅ Настроить URL routing
- ✅ Добавить фильтрацию и поиск

**Дополнительно:**

- ✅ Django Admin для всех моделей
- ✅ Кеширование (Redis)
- ✅ Тесты (models, API, tasks)
- ✅ API документация (Swagger)
- ✅ CORS настройки
- ✅ Rate limiting для заявок
- ✅ README с инструкциями

**Срок реализации:** 3-4 недели

---

## Важные файлы

- [`BACKEND_TECHNICAL_SPECIFICATION.md`](BACKEND_TECHNICAL_SPECIFICATION.md) - полное ТЗ с описанием всех таблиц и endpoints
- [`BUSINESS_DOCUMENTATION.md`](BUSINESS_DOCUMENTATION.md) - бизнес-логика основного приложения
- [`BUSINESS_METRICS_ANALYSIS.md`](BUSINESS_METRICS_ANALYSIS.md) - анализ метрик для сайта
- [`business_metrics_report.json`](business_metrics_report.json) - данные метрик из БД