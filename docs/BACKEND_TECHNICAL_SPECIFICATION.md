# Техническое задание: Backend для корпоративного сайта 911

**Версия:** 1.0  
**Дата создания:** 2025-12-26  
**Цель:** Разработка REST API для корпоративного сайта с автоматической синхронизацией с основным приложением

---

## 📋 Содержание

1. [Общее описание](#общее-описание)
2. [Архитектура и стек технологий](#архитектура-и-стек-технологий)
3. [Структура базы данных](#структура-базы-данных)
4. [API Endpoints](#api-endpoints)
5. [Бизнес-логика](#бизнес-логика)
6. [План реализации](#план-реализации)

---

## 📖 Общее описание

### Назначение системы

Backend для корпоративного сайта, который будет:
- Предоставлять публичное API для отображения информации о услугах, городах, метриках
- Синхронизироваться с основной БД приложения (использовать существующие таблицы где возможно)
- Обрабатывать заявки с сайта и интегрироваться с мобильным приложением
- Управлять контентом для SEO-оптимизации

### Ключевые требования

1. **Расширенная версия:** Единая база данных с приложением
2. **Автоматизация:** Новые города из приложения автоматически отображаются на сайте
3. **SEO-оптимизация:** Управление meta-тегами, slug'ами, контентом
4. **Производительность:** Кеширование, оптимизация запросов
5. **Аналитика:** Интеграция с существующими метриками

---

## 🏗️ Архитектура и стек технологий

### Backend Framework

- **Django 5.0.3** + **Django REST Framework**
- **PostgreSQL** - основная БД (общая с приложением)
- **Redis** - кеширование API responses
- **Celery** - фоновые задачи (обновление метрик, синхронизация)

### Интеграция с существующей системой

**Повторное использование таблиц:**
- `city_db` - города
- `service_db` - услуги  
- `option_db` - опции услуг
- `option_price_db` - цены опций по городам
- `partner_db` - данные партнеров (для метрик)
- `review_db` - отзывы
- `order_db` - заказы (для метрик)

**Новые таблицы:**
- `website_city_content` - контент для страниц городов
- `website_service_content` - контент для страниц услуг
- `website_advantage` - преимущества платформы
- `website_metric` - метрики для отображения на сайте
- `website_contact` - контактная информация
- `website_seo_meta` - SEO метаданные
- `website_app_link` - ссылки на приложения
- `website_lead` - заявки с сайта

---

## 🗄️ Структура базы данных

### 1. Таблица: website_city_content

**Назначение:** Контент для страниц городов на сайте

```sql
CREATE TABLE website_city_content (
    id SERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL REFERENCES city_db(id) ON DELETE CASCADE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- SEO контент
    title VARCHAR(255),
    meta_description TEXT,
    h1_title VARCHAR(255),
    
    -- Основной контент
    short_description TEXT,
    full_description TEXT,  -- HTML-разметка
    advantages_html TEXT,   -- HTML блок преимуществ для этого города
    
    -- Дополнительная информация
    partner_count INTEGER DEFAULT 0,  -- Кеш: количество партнеров
    avg_rating DECIMAL(3,2) DEFAULT 0.00,  -- Кеш: средний рейтинг
    review_count INTEGER DEFAULT 0,  -- Кеш: количество отзывов
    
    -- Служебные поля
    display_order INTEGER DEFAULT 0,  -- Порядок отображения
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_city_slug (slug),
    INDEX idx_city_active (is_active),
    UNIQUE INDEX idx_city_unique (city_id)
);
```

**Связи:**
- `city_id` → `city_db.id` (один город = одна запись контента)

---

### 2. Таблица: website_service_content

**Назначение:** Контент для страниц услуг на сайте

```sql
CREATE TABLE website_service_content (
    id SERIAL PRIMARY KEY,
    service_id BIGINT NOT NULL REFERENCES service_db(id) ON DELETE CASCADE,
    city_id BIGINT REFERENCES city_db(id) ON DELETE CASCADE,  -- NULL = общая для всех городов
    slug VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- SEO контент
    title VARCHAR(255),
    meta_description TEXT,
    h1_title VARCHAR(255),
    
    -- Основной контент
    short_description TEXT,
    full_description TEXT,  -- HTML-разметка
    how_it_works_html TEXT,  -- Блок "Как это работает"
    benefits_html TEXT,  -- Преимущества услуги
    
    -- Прайс-лист (опционально, если не хватает option_price_db)
    price_list_html TEXT,
    
    -- Изображения
    icon_url VARCHAR(255),
    cover_image_url VARCHAR(255),
    
    -- Служебные поля
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_service_slug (slug),
    INDEX idx_service_active (is_active),
    INDEX idx_service_city (city_id),
    UNIQUE INDEX idx_service_city_unique (service_id, city_id)
);
```

**Связи:**
- `service_id` → `service_db.id`
- `city_id` → `city_db.id` (NULL для общего описания услуги)

**Бизнес-логика:**
- Если `city_id` IS NULL → общее описание услуги
- Если `city_id` задан → описание услуги для конкретного города

---

### 3. Таблица: website_advantage

**Назначение:** Преимущества платформы (для блока "Наши преимущества")

```sql
CREATE TABLE website_advantage (
    id SERIAL PRIMARY KEY,
    target_audience VARCHAR(20) NOT NULL,  -- 'client', 'partner', 'both'
    
    -- Контент
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_name VARCHAR(50),  -- Название иконки (для frontend)
    
    -- Отображение
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    
    -- Служебные поля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_advantage_audience (target_audience),
    INDEX idx_advantage_active (is_active)
);
```

**Примеры данных:**
- "Быстрый отклик" (target: client)
- "Работа 24/7" (target: both)
- "Прозрачная комиссия" (target: partner)

---

### 4. Таблица: website_metric

**Назначение:** Метрики для отображения на сайте

```sql
CREATE TABLE website_metric (
    id SERIAL PRIMARY KEY,
    metric_key VARCHAR(100) NOT NULL UNIQUE,  -- 'total_cities', 'total_partners', etc.
    
    -- Значение и описание
    value VARCHAR(100),  -- "82", "195", "4.84/5"
    display_label VARCHAR(255),  -- "Городов присутствия"
    description TEXT,  -- Подробное описание
    
    -- Тип метрики
    metric_type VARCHAR(50),  -- 'platform', 'partner', 'client', 'city', 'service'
    
    -- Отображение
    is_visible_on_site BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    icon_name VARCHAR(50),
    
    -- Автообновление
    is_auto_calculated BOOLEAN DEFAULT FALSE,  -- Если TRUE, обновляется Celery задачей
    last_calculated_at TIMESTAMP,
    
    -- Служебные поля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_metric_key (metric_key),
    INDEX idx_metric_visible (is_visible_on_site),
    INDEX idx_metric_type (metric_type)
);
```

**Примеры данных:**
```json
{
  "metric_key": "total_cities",
  "value": "82",
  "display_label": "Городов присутствия",
  "metric_type": "platform",
  "is_auto_calculated": true
}
```

---

### 5. Таблица: website_contact

**Назначение:** Контактная информация для разных соц. сетей и платформ

```sql
CREATE TABLE website_contact (
    id SERIAL PRIMARY KEY,
    contact_type VARCHAR(50) NOT NULL,  -- 'phone', 'email', 'telegram', 'whatsapp', 'vk', 'instagram', etc.
    
    -- Контакт
    value VARCHAR(255) NOT NULL,  -- Номер телефона, username, ссылка
    label VARCHAR(255),  -- Отображаемое название
    
    -- Для приложений
    is_app_store_link BOOLEAN DEFAULT FALSE,
    platform VARCHAR(20),  -- 'ios', 'android'
    
    -- Отображение
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    icon_name VARCHAR(50),
    
    -- Служебные поля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_contact_type (contact_type),
    INDEX idx_contact_active (is_active)
);
```

**Примеры данных:**
```json
[
  {"contact_type": "phone", "value": "+7 (999) 123-45-67", "label": "Горячая линия"},
  {"contact_type": "whatsapp", "value": "https://wa.me/79991234567", "label": "WhatsApp"},
  {"contact_type": "telegram", "value": "@911_support", "label": "Telegram"},
  {"contact_type": "app_store", "value": "https://apps.apple.com/...", "platform": "ios", "is_app_store_link": true},
  {"contact_type": "google_play", "value": "https://play.google.com/...", "platform": "android", "is_app_store_link": true}
]
```

---

### 6. Таблица: website_seo_meta

**Назначение:** SEO метаданные для страниц сайта

```sql
CREATE TABLE website_seo_meta (
    id SERIAL PRIMARY KEY,
    page_type VARCHAR(50) NOT NULL,  -- 'home', 'city', 'service', 'city_service', 'about', 'contacts'
    
    -- Связи (nullable для общих страниц)
    city_id BIGINT REFERENCES city_db(id) ON DELETE CASCADE,
    service_id BIGINT REFERENCES service_db(id) ON DELETE CASCADE,
    
    -- SEO поля
    title VARCHAR(255) NOT NULL,  -- <title>
    meta_description TEXT,  -- <meta name="description">
    meta_keywords TEXT,  -- <meta name="keywords"> (устарело, но иногда используется)
    h1_title VARCHAR(255),  -- Заголовок H1 на странице
    canonical_url VARCHAR(255),  -- Канонический URL
    
    -- Open Graph
    og_title VARCHAR(255),
    og_description TEXT,
    og_image_url VARCHAR(255),
    
    -- Структурированные данные
    schema_json JSONB,  -- Schema.org разметка
    
    -- Полный slug страницы
    full_slug VARCHAR(255) NOT NULL UNIQUE,  -- '/city/moscow', '/service/tire-service', '/city/moscow/tire-service'
    
    -- Служебные поля
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_seo_page_type (page_type),
    INDEX idx_seo_slug (full_slug),
    INDEX idx_seo_city (city_id),
    INDEX idx_seo_service (service_id),
    UNIQUE INDEX idx_seo_unique (page_type, city_id, service_id)
);
```

**Примеры slugs:**
- `/` - главная
- `/cities` - список городов
- `/cities/moscow` - страница Москвы
- `/services/tire-service` - страница услуги "Шиномонтаж"
- `/cities/moscow/tire-service` - страница "Шиномонтаж в Москве"

---

### 7. Таблица: website_app_link

**Назначение:** Ссылки на приложения в магазинах (отдельная таблица для гибкости)

```sql
CREATE TABLE website_app_link (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,  -- 'ios', 'android'
    app_type VARCHAR(20) NOT NULL,  -- 'client', 'partner'
    
    -- Ссылки
    store_url VARCHAR(255) NOT NULL,
    direct_download_url VARCHAR(255),
    
    -- Версия приложения (синхронизация с mobile_app_versions_db)
    version VARCHAR(20),
    
    -- QR-код
    qr_code_url VARCHAR(255),
    
    -- Отображение
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    
    -- Служебные поля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_app_platform (platform),
    INDEX idx_app_type (app_type),
    UNIQUE INDEX idx_app_unique (platform, app_type)
);
```

---

### 8. Таблица: website_lead

**Назначение:** Заявки с сайта

```sql
CREATE TABLE website_lead (
    id SERIAL PRIMARY KEY,
    
    -- Данные клиента
    name VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    
    -- Что интересует
    city_id BIGINT REFERENCES city_db(id) ON DELETE SET NULL,
    service_id BIGINT REFERENCES service_db(id) ON DELETE SET NULL,
    message TEXT,
    
    -- Источник
    source_page VARCHAR(255),  -- URL страницы, откуда пришла заявка
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Статус обработки
    status VARCHAR(20) DEFAULT 'new',  -- 'new', 'processing', 'converted', 'rejected'
    processed_at TIMESTAMP,
    processed_by_user_id BIGINT,
    
    -- Интеграция с приложением
    is_synced_to_app BOOLEAN DEFAULT FALSE,
    app_order_id BIGINT REFERENCES order_db(id) ON DELETE SET NULL,
    
    -- Служебные поля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_lead_status (status),
    INDEX idx_lead_city (city_id),
    INDEX idx_lead_service (service_id),
    INDEX idx_lead_created (created_at)
);
```

---

### 9. Связь с существующей таблицей option_price_db

**Используем существующую структуру:**

```sql
-- Существующая таблица (из дампа БД)
CREATE TABLE option_price_db (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(15,2) NOT NULL,
    city_id BIGINT NOT NULL REFERENCES city_db(id),
    option_id BIGINT NOT NULL REFERENCES option_db(id),
    technic_category_id BIGINT REFERENCES technic_category_db(id),
    
    UNIQUE (option_id, city_id, technic_category_id)
);
```

**Дополнительное поле для сайта (опционально, через расширение):**

Можно добавить таблицу `website_option_price_display`:

```sql
CREATE TABLE website_option_price_display (
    id SERIAL PRIMARY KEY,
    option_price_id BIGINT NOT NULL REFERENCES option_price_db(id) ON DELETE CASCADE UNIQUE,
    
    -- Дополнительное описание для сайта
    display_name VARCHAR(255),  -- Переопределенное название для сайта
    description TEXT,
    
    -- Отображение
    is_visible_on_site BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 API Endpoints

### Группа: Города (Cities)

#### 1. GET /api/website/cities/

**Описание:** Получить список городов для отображения на сайте

**Query параметры:**
- `is_active` (boolean) - фильтр по активности (из website_city_content)
- `has_partners` (boolean) - только города с партнерами
- `has_services` (boolean) - только города с доступными услугами
- `ordering` (string) - сортировка: 'name', '-partner_count', 'display_order'
- `search` (string) - поиск по названию города

**Response:**
```json
{
  "count": 82,
  "results": [
    {
      "id": 34,
      "title": "Москва",
      "slug": "moscow",
      "is_active": true,
      "partner_count": 5,
      "avg_rating": 4.75,
      "review_count": 234,
      "short_description": "Экстренные автоуслуги в Москве 24/7",
      "services_available": [1, 2, 3, 4]  // ID услуг
    }
  ]
}
```

---

#### 2. GET /api/website/cities/{slug}/

**Описание:** Получить детальную информацию о городе

**Path параметры:**
- `slug` - slug города (например, "moscow")

**Response:**
```json
{
  "id": 34,
  "title": "Москва",
  "slug": "moscow",
  "is_active": true,
  
  "seo": {
    "title": "Экстренные автоуслуги в Москве 24/7 | 911",
    "meta_description": "Выездной шиномонтаж, эвакуатор, доставка топлива...",
    "h1_title": "Автоуслуги в Москве",
    "canonical_url": "/cities/moscow"
  },
  
  "content": {
    "short_description": "...",
    "full_description": "<h2>О сервисе...</h2><p>...",
    "advantages_html": "<ul><li>..."
  },
  
  "statistics": {
    "partner_count": 5,
    "active_partners": 4,
    "avg_rating": 4.75,
    "review_count": 234,
    "completed_orders": 1250
  },
  
  "services": [
    {
      "id": 1,
      "title": "Выездной шиномонтаж",
      "slug": "tire-service",
      "icon_url": "/media/icons/tire.svg",
      "short_description": "..."
    }
  ],
  
  "working_zones": [
    {
      "id": 1,
      "title": "Центр Москвы",
      "departure_price": 500.00
    }
  ]
}
```

---

### Группа: Услуги (Services)

#### 3. GET /api/website/services/

**Описание:** Получить список услуг

**Query параметры:**
- `city_id` (integer) - фильтр по городу
- `city_slug` (string) - фильтр по slug города
- `is_active` (boolean) - только активные
- `ordering` (string) - сортировка

**Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "title": "Выездной шиномонтаж",
      "slug": "tire-service",
      "icon_url": "/media/icons/tire.svg",
      "short_description": "Быстрый выезд мастера к вам",
      "cities_available": 82,
      "avg_price_from": 500.00
    }
  ]
}
```

---

#### 4. GET /api/website/services/{slug}/

**Описание:** Получить детальную информацию об услуге

**Query параметры:**
- `city_id` (integer) - для получения информации в контексте города
- `city_slug` (string) - альтернатива city_id

**Response (без города):**
```json
{
  "id": 1,
  "title": "Выездной шиномонтаж",
  "slug": "tire-service",
  
  "seo": {
    "title": "Выездной шиномонтаж | 911",
    "meta_description": "...",
    "h1_title": "Выездной шиномонтаж"
  },
  
  "content": {
    "short_description": "...",
    "full_description": "<h2>...",
    "how_it_works_html": "<ol><li>...",
    "benefits_html": "<ul><li>..."
  },
  
  "statistics": {
    "cities_available": 82,
    "partner_count": 120,
    "completed_orders": 5420
  },
  
  "price_range": {
    "min": 400.00,
    "max": 1500.00,
    "currency": "RUB"
  }
}
```

**Response (с городом):**
```json
{
  // ... все поля выше ...
  
  "city_specific": {
    "city_id": 34,
    "city_name": "Москва",
    "partner_count": 5,
    "avg_rating": 4.75,
    
    "options": [
      {
        "id": 15,
        "title": "Снять/поставить колесо (4 шт)",
        "price": 500.00,
        "technic_categories": [
          {"id": 1, "title": "Легковой", "price": 500.00},
          {"id": 2, "title": "Внедорожник", "price": 700.00}
        ]
      }
    ]
  }
}
```

---

#### 5. GET /api/website/cities/{city_slug}/services/{service_slug}/

**Описание:** Получить информацию об услуге в конкретном городе (комбинированная страница)

**Response:**
```json
{
  "city": {
    "id": 34,
    "title": "Москва",
    "slug": "moscow"
  },
  
  "service": {
    "id": 1,
    "title": "Выездной шиномонтаж",
    "slug": "tire-service"
  },
  
  "seo": {
    "title": "Выездной шиномонтаж в Москве 24/7 | 911",
    "meta_description": "...",
    "h1_title": "Шиномонтаж в Москве",
    "full_slug": "/cities/moscow/tire-service"
  },
  
  "content": {
    "description": "...",  // Специфичное для города описание
    "advantages": "..."
  },
  
  "statistics": {
    "partner_count": 5,
    "avg_rating": 4.75,
    "completed_orders": 156,
    "avg_response_time_minutes": 25
  },
  
  "pricing": {
    "options": [
      {
        "option_id": 15,
        "title": "Снять/поставить колесо (4 шт)",
        "categories": [
          {
            "category_id": 1,
            "category_title": "Легковой",
            "price": 500.00
          },
          {
            "category_id": 2,
            "category_title": "Внедорожник",
            "price": 700.00
          }
        ]
      }
    ],
    "delivery_price": 300.00
  },
  
  "reviews": [
    {
      "id": 45,
      "rating": 5,
      "comment": "Отличный сервис!",
      "created_at": "2025-12-20T10:30:00Z",
      "partner_name": "Иван И."
    }
  ]
}
```

---

### Группа: Опции и цены (Options & Pricing)

#### 6. GET /api/website/options/

**Описание:** Получить список опций услуг с ценами

**Query параметры:**
- `service_id` (integer) - фильтр по услуге
- `city_id` (integer) - фильтр по городу
- `city_slug` (string) - альтернатива city_id
- `technic_category_id` (integer) - фильтр по категории техники

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "option_id": 15,
      "option_title": "Снять/поставить колесо (4 шт)",
      "service_id": 1,
      "service_title": "Выездной шиномонтаж",
      "city_id": 34,
      "city_name": "Москва",
      "technic_category_id": 1,
      "technic_category_title": "Легковой",
      "price": 500.00,
      "display_name": "Снятие и установка колес",
      "description": "Полный комплект из 4х колес"
    }
  ]
}
```

---

### Группа: Преимущества (Advantages)

#### 7. GET /api/website/advantages/

**Описание:** Получить список преимуществ платформы

**Query параметры:**
- `target_audience` (string) - фильтр: 'client', 'partner', 'both'
- `is_active` (boolean) - только активные

**Response:**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "title": "Быстрый отклик",
      "description": "Партнеры получают уведомление моментально",
      "icon_name": "lightning",
      "target_audience": "client",
      "display_order": 1
    },
    {
      "id": 2,
      "title": "Работа 24/7",
      "description": "Услуги доступны круглосуточно",
      "icon_name": "clock",
      "target_audience": "both",
      "display_order": 2
    }
  ]
}
```

---

### Группа: Метрики (Metrics)

#### 8. GET /api/website/metrics/

**Описание:** Получить метрики для отображения на сайте

**Query параметры:**
- `metric_type` (string) - фильтр: 'platform', 'partner', 'client', 'city', 'service'
- `is_visible` (boolean) - только видимые на сайте
- `city_id` (integer) - метрики для конкретного города

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "metric_key": "total_cities",
      "value": "82",
      "display_label": "Городов присутствия",
      "description": "Работаем в 82 городах России",
      "metric_type": "platform",
      "icon_name": "map-pin",
      "display_order": 1
    },
    {
      "metric_key": "total_partners",
      "value": "195",
      "display_label": "Проверенных партнеров",
      "metric_type": "platform",
      "icon_name": "users",
      "display_order": 2
    },
    {
      "metric_key": "avg_review_rating",
      "value": "4.84/5",
      "display_label": "Средняя оценка",
      "metric_type": "platform",
      "icon_name": "star",
      "display_order": 3
    }
  ]
}
```

---

### Группа: Контакты (Contacts)

#### 9. GET /api/website/contacts/

**Описание:** Получить контактную информацию

**Query параметры:**
- `contact_type` (string) - фильтр: 'phone', 'email', 'telegram', 'whatsapp', etc.
- `is_app_link` (boolean) - только ссылки на приложения
- `is_active` (boolean) - только активные

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "contact_type": "phone",
      "value": "+7 (999) 123-45-67",
      "label": "Горячая линия",
      "icon_name": "phone",
      "display_order": 1
    },
    {
      "id": 2,
      "contact_type": "whatsapp",
      "value": "https://wa.me/79991234567",
      "label": "WhatsApp",
      "icon_name": "whatsapp",
      "display_order": 2
    },
    {
      "id": 5,
      "contact_type": "app_store",
      "value": "https://apps.apple.com/...",
      "label": "Скачать в App Store",
      "is_app_store_link": true,
      "platform": "ios",
      "icon_name": "apple",
      "display_order": 10
    }
  ]
}
```

---

### Группа: Ссылки на приложения (App Links)

#### 10. GET /api/website/app-links/

**Описание:** Получить ссылки на мобильные приложения

**Query параметры:**
- `platform` (string) - фильтр: 'ios', 'android'
- `app_type` (string) - фильтр: 'client', 'partner'

**Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "platform": "ios",
      "app_type": "client",
      "store_url": "https://apps.apple.com/...",
      "version": "2.5.0",
      "qr_code_url": "/media/qr/ios_client.png"
    },
    {
      "id": 2,
      "platform": "android",
      "app_type": "client",
      "store_url": "https://play.google.com/...",
      "version": "2.5.1",
      "qr_code_url": "/media/qr/android_client.png"
    }
  ]
}
```

---

### Группа: Заявки (Leads)

#### 11. POST /api/website/leads/

**Описание:** Создать заявку с сайта

**Request Body:**
```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "city_id": 34,
  "service_id": 1,
  "message": "Нужен выездной шиномонтаж завтра в 10:00",
  "source_page": "/cities/moscow/tire-service",
  "utm_source": "yandex",
  "utm_medium": "cpc",
  "utm_campaign": "moscow_tire"
}
```

**Response:**
```json
{
  "id": 123,
  "status": "new",
  "message": "Заявка принята. Мы свяжемся с вами в ближайшее время.",
  "created_at": "2025-12-26T15:30:00Z"
}
```

---

### Группа: SEO (для frontend)

#### 12. GET /api/website/seo-meta/

**Описание:** Получить SEO метаданные для страницы

**Query параметры:**
- `page_type` (string) - тип страницы: 'home', 'city', 'service', 'city_service', etc.
- `city_slug` (string) - slug города (если применимо)
- `service_slug` (string) - slug услуги (если применимо)
- `full_slug` (string) - полный slug страницы

**Response:**
```json
{
  "page_type": "city_service",
  "full_slug": "/cities/moscow/tire-service",
  
  "seo": {
    "title": "Выездной шиномонтаж в Москве 24/7 | 911",
    "meta_description": "Выездной шиномонтаж в Москве. Быстрый приезд мастера, доступные цены, работа 24/7. Звоните!",
    "meta_keywords": "шиномонтаж москва, выездной шиномонтаж, мобильный шиномонтаж",
    "h1_title": "Выездной шиномонтаж в Москве",
    "canonical_url": "/cities/moscow/tire-service"
  },
  
  "open_graph": {
    "og_title": "Выездной шиномонтаж в Москве 24/7",
    "og_description": "...",
    "og_image_url": "/media/og/moscow-tire.jpg"
  },
  
  "schema_json": {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Выездной шиномонтаж",
    "provider": {
      "@type": "Organization",
      "name": "911"
    }
  }
}
```

---

### Группа: Отзывы (Reviews) - используем существующую таблицу

#### 13. GET /api/website/reviews/

**Описание:** Получить отзывы для отображения на сайте

**Query параметры:**
- `city_id` (integer) - отзывы по партнерам города
- `service_id` (integer) - отзывы по услуге (через заказы)
- `partner_id` (integer) - отзывы конкретного партнера
- `rating` (integer) - фильтр по оценке (1-5)
- `has_comment` (boolean) - только с текстом
- `limit` (integer) - количество отзывов (default: 10)
- `ordering` (string) - сортировка: '-created_at', '-rating'

**Response:**
```json
{
  "count": 2728,
  "results": [
    {
      "id": 45,
      "rating": 5,
      "comment": "Отличный сервис, всё супер",
      "created_at": "2024-12-21T15:40:17Z",
      "client_name": "Тимур",  // Если есть
      "partner": {
        "id": 23,
        "first_name": "Иван",
        "last_name": "И.",  // Скрыто для приватности
        "rating": 4.85
      }
    }
  ]
}
```

---

## 🔧 Бизнес-логика

### 1. Автоматическая синхронизация городов

**Задача:** При добавлении города в `city_db` (через админку приложения), автоматически создавать запись в `website_city_content`.

**Реализация:**
- Django Signal `post_save` на модели `City`
- Celery задача для создания базового контента

```python
@receiver(post_save, sender=City)
def create_city_content(sender, instance, created, **kwargs):
    if created:
        # Создаем базовый контент для сайта
        WebsiteCityContent.objects.get_or_create(
            city_id=instance.id,
            defaults={
                'slug': slugify(instance.title),
                'is_active': False,  # Требует наполнения контентом
                'title': f"Автоуслуги в {instance.title}",
                'short_description': f"Экстренные автоуслуги в городе {instance.title}"
            }
        )
```

---

### 2. Обновление метрик

**Задача:** Автоматически обновлять метрики на сайте.

**Реализация:**
- Celery Periodic Task (каждый час или по расписанию)
- Пересчет метрик из основных таблиц

```python
@shared_task
def update_website_metrics():
    # Обновление общих метрик
    WebsiteMetric.objects.update_or_create(
        metric_key='total_cities',
        defaults={
            'value': str(City.objects.count()),
            'last_calculated_at': timezone.now()
        }
    )
    
    # Обновление метрик партнеров
    confirmed_partners = Partner.objects.filter(verify='confirmed').count()
    WebsiteMetric.objects.update_or_create(
        metric_key='total_partners',
        defaults={
            'value': str(confirmed_partners),
            'last_calculated_at': timezone.now()
        }
    )
    
    # И т.д. для всех метрик
```

---

### 3. Кеширование данных в WebsiteCityContent

**Задача:** Хранить кешированные данные (partner_count, avg_rating) для быстрого отображения.

**Реализация:**
- Celery задача обновления кеша
- Периодический пересчет (раз в день или при изменении данных)

```python
@shared_task
def update_city_cache(city_id):
    city_content = WebsiteCityContent.objects.get(city_id=city_id)
    
    # Обновляем количество партнеров
    partner_count = Partner.objects.filter(
        city_id=city_id,
        verify='confirmed'
    ).count()
    
    # Обновляем средний рейтинг
    partners = Partner.objects.filter(city_id=city_id, verify='confirmed')
    avg_rating = partners.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Обновляем количество отзывов
    partner_ids = partners.values_list('id', flat=True)
    review_count = Review.objects.filter(partner_id__in=partner_ids).count()
    
    city_content.partner_count = partner_count
    city_content.avg_rating = avg_rating
    city_content.review_count = review_count
    city_content.save()
```

---

### 4. Интеграция заявок с приложением

**Задача:** Заявка с сайта должна попадать в основную систему заказов.

**Реализация:**
- При создании `WebsiteLead` запускается Celery задача
- Задача создает `Client` (если не существует) и `Order`

```python
@shared_task
def process_website_lead(lead_id):
    lead = WebsiteLead.objects.get(id=lead_id)
    
    # Найти или создать клиента по телефону
    user, _ = CustomUser.objects.get_or_create(phone=lead.phone)
    client, _ = Client.objects.get_or_create(
        current_user=user,
        defaults={'first_name': lead.name}
    )
    
    # Создать заказ (если есть достаточно информации)
    if lead.city_id and lead.service_id:
        order = Order.objects.create(
            client=client,
            city_id=lead.city_id,
            service_id=lead.service_id,
            comment=lead.message,
            status='new',
            # ... другие поля
        )
        
        lead.is_synced_to_app = True
        lead.app_order_id = order.id
        lead.save()
```

---

### 5. SEO: Автоматическая генерация slug'ов

**Задача:** При создании города или услуги автоматически генерировать SEO-friendly slug.

**Реализация:**
- Использовать `django.utils.text.slugify` с транслитерацией
- Обеспечить уникальность slug'ов

```python
from django.utils.text import slugify
from transliterate import translit

def generate_unique_slug(title, model_class, field_name='slug'):
    # Транслитерация и slugify
    base_slug = slugify(translit(title, 'ru', reversed=True))
    slug = base_slug
    counter = 1
    
    # Проверка уникальности
    while model_class.objects.filter(**{field_name: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug
```

---

### 6. Фильтрация активных городов и услуг

**Задача:** Показывать на сайте только активные города с доступными услугами.

**Реализация в API:**

```python
class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    
    def get_queryset(self):
        queryset = WebsiteCityContent.objects.filter(is_active=True)
        
        # Фильтр: только города с партнерами
        if self.request.query_params.get('has_partners'):
            queryset = queryset.filter(partner_count__gt=0)
        
        # Фильтр: только города с услугами
        if self.request.query_params.get('has_services'):
            queryset = queryset.filter(
                city__prices__isnull=False
            ).distinct()
        
        return queryset
```

---

## 📋 План реализации

### Этап 1: Подготовка (1-2 дня)

**Задачи:**
1. ✅ Создать отдельный Django app: `website_api`
2. ✅ Настроить структуру проекта
3. ✅ Добавить зависимости в `requirements.txt` или `pyproject.toml`

**Команды:**
```bash
cd 911-develop
python manage.py startapp website_api
```

---

### Этап 2: Миграции БД (2-3 дня)

**Задачи:**
1. ✅ Создать модели для новых таблиц
2. ✅ Создать миграции
3. ✅ Применить миграции
4. ✅ Заполнить таблицы начальными данными (fixtures)

**Файлы для создания:**
- `website_api/models/__init__.py`
- `website_api/models/city_content.py`
- `website_api/models/service_content.py`
- `website_api/models/advantage.py`
- `website_api/models/metric.py`
- `website_api/models/contact.py`
- `website_api/models/seo_meta.py`
- `website_api/models/app_link.py`
- `website_api/models/lead.py`

**Команды:**
```bash
python manage.py makemigrations website_api
python manage.py migrate website_api
python manage.py loaddata website_api/fixtures/initial_data.json
```

---

### Этап 3: Serializers (2 дня)

**Задачи:**
1. ✅ Создать serializers для всех моделей
2. ✅ Добавить вложенные serializers для связанных данных
3. ✅ Добавить read-only поля для вычисляемых данных

**Файлы для создания:**
- `website_api/serializers/__init__.py`
- `website_api/serializers/city_serializers.py`
- `website_api/serializers/service_serializers.py`
- `website_api/serializers/advantage_serializers.py`
- `website_api/serializers/metric_serializers.py`
- `website_api/serializers/contact_serializers.py`
- `website_api/serializers/seo_serializers.py`
- `website_api/serializers/lead_serializers.py`
- `website_api/serializers/review_serializers.py`

---

### Этап 4: Views и ViewSets (3-4 дня)

**Задачи:**
1. ✅ Создать ViewSets для всех endpoints
2. ✅ Реализовать фильтрацию (django-filter)
3. ✅ Реализовать поиск
4. ✅ Добавить пагинацию
5. ✅ Оптимизировать запросы (select_related, prefetch_related)

**Файлы для создания:**
- `website_api/views/__init__.py`
- `website_api/views/city_views.py`
- `website_api/views/service_views.py`
- `website_api/views/advantage_views.py`
- `website_api/views/metric_views.py`
- `website_api/views/contact_views.py`
- `website_api/views/lead_views.py`
- `website_api/views/review_views.py`

---

### Этап 5: URL Routing (1 день)

**Задачи:**
1. ✅ Настроить URL patterns
2. ✅ Использовать DefaultRouter для ViewSets
3. ✅ Добавить версионирование API (опционально)

**Файлы для создания:**
- `website_api/urls.py`

**Обновить:**
- `config/urls.py` - добавить `path('api/website/', include('website_api.urls'))`

---

### Этап 6: Celery Tasks (2-3 дня)

**Задачи:**
1. ✅ Создать задачу автоматического создания `WebsiteCityContent`
2. ✅ Создать задачу обновления метрик
3. ✅ Создать задачу обновления кеша городов
4. ✅ Создать задачу обработки заявок
5. ✅ Настроить периодические задачи (Celery Beat)

**Файлы для создания:**
- `website_api/tasks/__init__.py`
- `website_api/tasks/sync_tasks.py`
- `website_api/tasks/metrics_tasks.py`
- `website_api/tasks/cache_tasks.py`
- `website_api/tasks/lead_tasks.py`

---

### Этап 7: Django Signals (1 день)

**Задачи:**
1. ✅ Создать signal для автосоздания `WebsiteCityContent` при создании `City`
2. ✅ Создать signal для обработки `WebsiteLead` после создания

**Файлы для создания:**
- `website_api/signals.py`

**Обновить:**
- `website_api/apps.py` - подключить signals в `ready()`

---

### Этап 8: Админ-панель (1-2 дня)

**Задачи:**
1. ✅ Настроить Django Admin для всех моделей
2. ✅ Добавить фильтры, поиск, сортировку
3. ✅ Добавить inline редактирование
4. ✅ Добавить кнопки для ручного обновления метрик/кеша

**Файлы для создания:**
- `website_api/admin/__init__.py`
- `website_api/admin/city_admin.py`
- `website_api/admin/service_admin.py`
- `website_api/admin/advantage_admin.py`
- `website_api/admin/metric_admin.py`
- `website_api/admin/contact_admin.py`
- `website_api/admin/seo_admin.py`
- `website_api/admin/lead_admin.py`

---

### Этап 9: Кеширование (1-2 дня)

**Задачи:**
1. ✅ Настроить Redis для кеширования
2. ✅ Добавить кеширование для списков (cities, services)
3. ✅ Добавить кеширование для детальных страниц
4. ✅ Настроить TTL для кеша
5. ✅ Добавить инвалидацию кеша при обновлении данных

**Пример:**
```python
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class CityListView(generics.ListAPIView):
    @method_decorator(cache_page(60 * 15))  # 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

---

### Этап 10: Тестирование (2-3 дня)

**Задачи:**
1. ✅ Написать unit tests для моделей
2. ✅ Написать API tests для endpoints
3. ✅ Протестировать фильтры и поиск
4. ✅ Протестировать Celery задачи
5. ✅ Проверить производительность (n+1 queries)

**Файлы для создания:**
- `website_api/tests/__init__.py`
- `website_api/tests/test_models.py`
- `website_api/tests/test_api.py`
- `website_api/tests/test_tasks.py`

---

### Этап 11: Документация API (1 день)

**Задачи:**
1. ✅ Настроить drf-spectacular (уже есть в проекте)
2. ✅ Добавить описания к endpoints
3. ✅ Добавить примеры запросов/ответов
4. ✅ Сгенерировать Swagger/ReDoc документацию

**Обновить:**
- Добавить docstrings к ViewSets
- Использовать `@extend_schema` для кастомизации документации

---

### Этап 12: Оптимизация и деплой (2 дня)

**Задачи:**
1. ✅ Оптимизировать SQL запросы
2. ✅ Добавить индексы в БД
3. ✅ Настроить CORS для frontend
4. ✅ Настроить rate limiting (защита от DDoS)
5. ✅ Подготовить fixtures с начальными данными
6. ✅ Развернуть на production

---

## 📦 Fixtures: Начальные данные

### Преимущества (Advantages)

```json
[
  {
    "model": "website_api.advantage",
    "pk": 1,
    "fields": {
      "target_audience": "client",
      "title": "Быстрый отклик",
      "description": "Партнеры получают уведомление моментально и выезжают к вам в кратчайшие сроки",
      "icon_name": "lightning",
      "is_active": true,
      "display_order": 1
    }
  },
  {
    "model": "website_api.advantage",
    "pk": 2,
    "fields": {
      "target_audience": "both",
      "title": "Работа 24/7",
      "description": "Услуги доступны круглосуточно, без выходных и праздников",
      "icon_name": "clock",
      "is_active": true,
      "display_order": 2
    }
  },
  {
    "model": "website_api.advantage",
    "pk": 3,
    "fields": {
      "target_audience": "client",
      "title": "Прозрачное ценообразование",
      "description": "Цена известна до начала работы, никаких скрытых платежей",
      "icon_name": "dollar-sign",
      "is_active": true,
      "display_order": 3
    }
  },
  {
    "model": "website_api.advantage",
    "pk": 4,
    "fields": {
      "target_audience": "client",
      "title": "Рейтинг и отзывы",
      "description": "Система оценок помогает выбрать лучших исполнителей",
      "icon_name": "star",
      "is_active": true,
      "display_order": 4
    }
  },
  {
    "model": "website_api.advantage",
    "pk": 5,
    "fields": {
      "target_audience": "partner",
      "title": "Стабильный поток заказов",
      "description": "Получайте заказы от клиентов в вашем городе",
      "icon_name": "trending-up",
      "is_active": true,
      "display_order": 5
    }
  },
  {
    "model": "website_api.advantage",
    "pk": 6,
    "fields": {
      "target_audience": "partner",
      "title": "Низкая комиссия",
      "description": "Прозрачная система комиссий без скрытых платежей",
      "icon_name": "percent",
      "is_active": true,
      "display_order": 6
    }
  }
]
```

### Метрики (Metrics)

```json
[
  {
    "model": "website_api.metric",
    "pk": 1,
    "fields": {
      "metric_key": "total_cities",
      "value": "82",
      "display_label": "Городов присутствия",
      "description": "Работаем в 82 городах России",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 1,
      "icon_name": "map-pin",
      "is_auto_calculated": true
    }
  },
  {
    "model": "website_api.metric",
    "pk": 2,
    "fields": {
      "metric_key": "total_partners",
      "value": "195",
      "display_label": "Проверенных партнеров",
      "description": "195 партнеров прошли верификацию и готовы помочь",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 2,
      "icon_name": "users",
      "is_auto_calculated": true
    }
  },
  {
    "model": "website_api.metric",
    "pk": 3,
    "fields": {
      "metric_key": "active_partners",
      "value": "155",
      "display_label": "Активных партнеров",
      "description": "155 партнеров готовы принять заказ прямо сейчас",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 3,
      "icon_name": "user-check",
      "is_auto_calculated": true
    }
  },
  {
    "model": "website_api.metric",
    "pk": 4,
    "fields": {
      "metric_key": "avg_review_rating",
      "value": "4.84/5",
      "display_label": "Средняя оценка",
      "description": "Средний рейтинг по отзывам клиентов",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 4,
      "icon_name": "star",
      "is_auto_calculated": true
    }
  },
  {
    "model": "website_api.metric",
    "pk": 5,
    "fields": {
      "metric_key": "total_reviews",
      "value": "2728",
      "display_label": "Отзывов",
      "description": "2728 отзывов от наших клиентов",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 5,
      "icon_name": "message-square",
      "is_auto_calculated": true
    }
  },
  {
    "model": "website_api.metric",
    "pk": 6,
    "fields": {
      "metric_key": "positive_reviews_percent",
      "value": "92%",
      "display_label": "Положительных отзывов",
      "description": "92% клиентов оценили сервис на 4-5 звезд",
      "metric_type": "platform",
      "is_visible_on_site": true,
      "display_order": 6,
      "icon_name": "thumbs-up",
      "is_auto_calculated": true
    }
  }
]
```

---

## 🚀 Итоговый чеклист

### Обязательные задачи

- [ ] Создать Django app `website_api`
- [ ] Создать модели для 9 новых таблиц
- [ ] Создать и применить миграции
- [ ] Создать serializers для всех моделей
- [ ] Создать ViewSets для 13 endpoints
- [ ] Настроить URL routing
- [ ] Создать Celery tasks (4 задачи)
- [ ] Настроить Django Signals (2 сигнала)
- [ ] Настроить Django Admin
- [ ] Настроить кеширование (Redis)
- [ ] Написать тесты
- [ ] Сгенерировать API документацию
- [ ] Создать fixtures с начальными данными
- [ ] Оптимизировать SQL запросы
- [ ] Настроить CORS
- [ ] Развернуть на production

### Дополнительные задачи

- [ ] Добавить версионирование API
- [ ] Настроить rate limiting
- [ ] Добавить логирование запросов
- [ ] Настроить мониторинг (Sentry)
- [ ] Создать CI/CD pipeline
- [ ] Написать документацию для разработчиков

---

**Общий срок реализации:** 3-4 недели (с учетом тестирования и оптимизации)

---

## 📝 Дополнительные заметки

1. **Безопасность:** Все публичные API endpoints должны быть read-only. POST запрос только для создания заявок.

2. **Производительность:** Использовать select_related и prefetch_related для оптимизации запросов.

3. **Кеширование:** Кешировать списки и детальные страницы на 15-60 минут.

4. **Мониторинг:** Логировать все заявки с сайта для аналитики.

5. **SEO:** Обеспечить быстрые ответы API (< 200ms) для лучшего SEO.

6. **Масштабируемость:** Использовать пагинацию для всех списков.

---

**Документ готов к использованию AI-ассистентом (Cursor) для автоматической генерации кода.**

