# Отчет о состоянии API бекенда 911

**Дата проверки:** 27 декабря 2025  
**Статус:** ✅ Бекенд работает корректно

## 📊 Общая информация

### Статус сервера
- **Контейнеры:** Запущены и работают (Docker Compose)
- **База данных:** PostgreSQL 15 (работает, healthy)
- **Веб-сервер:** Django Development Server на порту 8000 (работает, healthy)
- **CORS:** Настроен для разработки (разрешены все источники)
- **Режим:** Development (DEBUG=True)

### Доступность
- **Базовый URL:** `http://localhost:8000`
- **API URL:** `http://localhost:8000/api/website/`
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

## ✅ Подключение работает

**Фронтенд может подключиться к бекенду без ограничений**, так как:

1. ✅ CORS настроен на разрешение всех источников (`CORS_ALLOW_ALL_ORIGINS = True`)
2. ✅ Разрешены все HTTP методы (GET, POST, PUT, PATCH, DELETE)
3. ✅ Разрешены все стандартные заголовки
4. ✅ Сервер работает и отвечает на запросы
5. ✅ Порт 8000 открыт и доступен с хоста

## 🔧 Настройки CORS (Development)

```python
# /website_project/settings/dev.py

# Разрешены все источники для разработки
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Разрешены все методы
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Разрешены стандартные заголовки
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
```

## 📡 Доступные API эндпоинты

### 🏙️ Города
- `GET /api/website/cities/` - список городов присутствия
- `GET /api/website/cities/{slug}/` - детали города

### 🔧 Услуги
- `GET /api/website/services/` - список услуг
- `GET /api/website/services/{slug}/` - детали услуги
- `GET /api/website/services/{slug}/options/` - опции услуги

### 🏙️ + 🔧 Город + Услуга
- `GET /api/website/cities/{city_slug}/services/{service_slug}/` - информация об услуге в городе

### 🎯 Опции услуг
- `GET /api/website/options/` - список всех опций
- `GET /api/website/options/{id}/` - детали опции

### 🚗 Категории техники
- `GET /api/website/technic-categories/` - категории техники для эвакуатора
- `GET /api/website/technic-categories/{id}/` - детали категории

### ⭐ Преимущества
- `GET /api/website/advantages/` - преимущества платформы
- `GET /api/website/advantages/{id}/` - детали преимущества
- Фильтр: `?target_audience=client|partner|both`

### 📊 Метрики
- `GET /api/website/metrics/` - метрики платформы (города, клиенты, заказы и т.д.)
- `GET /api/website/metrics/{id}/` - детали метрики
- Фильтр: `?metric_type=platform|financial|operational|quality`

### 📞 Контакты
- `GET /api/website/contacts/` - контактная информация
- `GET /api/website/contacts/{id}/` - детали контакта
- Фильтр: `?contact_type=phone|email|address|social`

### 📱 Ссылки на приложения
- `GET /api/website/app-links/` - ссылки на мобильные приложения
- `GET /api/website/app-links/{id}/` - детали ссылки
- Фильтры: `?platform=ios|android`, `?app_type=client|partner`

### 🔍 SEO метаданные
- `GET /api/website/seo-meta/` - SEO метаданные для страниц
- `GET /api/website/seo-meta/{id}/` - детали метаданных
- Фильтры: `?page_type=home|city|service|city_service|about|contacts`
- Комплексный фильтр: `?city={id}&service={id}`

### 📝 Заявки (Лиды)
- `POST /api/website/leads/` - создать заявку (доступно без аутентификации)
- `GET /api/website/leads/` - список заявок (требует аутентификацию админа)
- `GET /api/website/leads/{id}/` - детали заявки (требует аутентификацию админа)
- Фильтры: `?status=new|processing|completed|cancelled`, `?city={id}`, `?service={id}`

## 🔄 Опциональная пагинация

API использует опциональную limit/offset пагинацию:

- **БЕЗ параметров** → возвращаются **ВСЕ записи** (без пагинации)
- **С параметрами** → применяется пагинация

**Параметры:**
- `?limit=20` - количество элементов (по умолчанию 20, максимум 100)
- `?offset=0` - смещение от начала (по умолчанию 0)

**Примеры:**
```
GET /api/website/cities/                    → все города
GET /api/website/cities/?limit=10           → первые 10 городов
GET /api/website/cities/?limit=50&offset=100 → города с 101 по 150
```

## 🎯 Фильтрация по активности

Все основные эндпоинты возвращают **только активные объекты** (`is_active=True`):
- Неактивные объекты не отображаются в списках
- Запрос неактивного объекта по ID/slug возвращает **404**

## 🔒 Аутентификация

**Для фронтенда:** Большинство эндпоинтов доступны **БЕЗ аутентификации**

**Требуют аутентификацию:**
- `GET /api/website/leads/` - список заявок (только для администраторов)
- `GET /api/website/leads/{id}/` - детали заявки (только для администраторов)

**Не требуют аутентификацию:**
- `POST /api/website/leads/` - создание заявки ✅

## 📋 Создание заявки

**Эндпоинт:** `POST /api/website/leads/`

**Обязательные поля:**
```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567"
}
```

**Опциональные поля:**
```json
{
  "email": "ivan@example.com",
  "city": 1,
  "service": 2,
  "message": "Нужен шиномонтаж завтра утром",
  "source_page": "/moskva/shinomontazh/",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "shinomontazh_moskva"
}
```

**Валидация:**
- `name`: 2-100 символов
- `phone`: 10-20 символов (форматы: +7..., 8..., и т.д.)
- `email`: валидный email (опционально)

**Статус:** По умолчанию создается со статусом `new`

## 🚫 Текущие ограничения

### Ограничений НЕТ для фронтенда в режиме разработки:

✅ CORS разрешает все источники  
✅ Все API эндпоинты доступны  
✅ Rate limiting НЕ включен (планируется)  
✅ Аутентификация не требуется для основных эндпоинтов  

### Планируемые ограничения (TODO):

1. **Rate Limiting для заявок**
   - Ограничение: 5 заявок в час с одного IP
   - Статус: Не реализовано (TODO в коде)
   
2. **Валидация телефона**
   - Более строгая валидация российских номеров
   - Статус: Базовая валидация работает

## 🧪 Проверка работоспособности

### Тест 1: Проверка метрик
```bash
curl http://localhost:8000/api/website/metrics/
# Ожидаемый результат: JSON с метриками (200 OK)
```

### Тест 2: Проверка городов
```bash
curl http://localhost:8000/api/website/cities/
# Ожидаемый результат: JSON со списком городов (200 OK)
```

### Тест 3: Проверка услуг
```bash
curl http://localhost:8000/api/website/services/
# Ожидаемый результат: JSON со списком услуг (200 OK)
```

### Тест 4: Создание заявки
```bash
curl -X POST http://localhost:8000/api/website/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовый пользователь",
    "phone": "+79991234567",
    "email": "test@example.com"
  }'
# Ожидаемый результат: JSON с созданной заявкой (201 Created)
```

### Тест 5: CORS preflight
```bash
curl -X OPTIONS http://localhost:8000/api/website/metrics/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v
# Ожидаемый результат: Заголовки Access-Control-Allow-* в ответе
```

## 🐳 Docker контейнеры

```bash
# Просмотр статуса
docker-compose -f docker-compose.dev.yml ps

# Результат:
NAME                        STATUS
911_backend_website-db-1    Up 2 hours (healthy)
911_backend_website-web-1   Up 2 hours (healthy)
```

```bash
# Просмотр логов
docker-compose -f docker-compose.dev.yml logs web --tail=50

# Результат: Логи успешно обработанных запросов
# Примеры:
# GET /api/website/metrics/ HTTP/1.1" 200
# GET /api/website/services/ HTTP/1.1" 200
```

## 🌐 Конфигурация для продакшена

Для продакшена используется отдельный файл настроек (`settings/prod.py`), который:

1. **Отключает DEBUG**
2. **Ограничивает CORS** конкретными доменами из переменной окружения
3. **Включает HTTPS** и защиту от XSS/CSRF
4. **Настраивает SMTP** для email уведомлений

**Переменные окружения для продакшена:**
```bash
DJANGO_SETTINGS_MODULE=website_project.settings.prod
ALLOWED_HOSTS=example.com,www.example.com
CORS_ALLOWED_ORIGINS=https://example.com,https://www.example.com
SECRET_KEY=your-secret-key-here
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=password
```

## 🎯 Рекомендации для фронтенда

### 1. Базовый URL
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### 2. Получение данных
```javascript
// Получить все города
fetch(`${API_BASE_URL}/api/website/cities/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Получить услугу по slug
fetch(`${API_BASE_URL}/api/website/services/shinomontazh/`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### 3. Создание заявки
```javascript
const createLead = async (leadData) => {
  const response = await fetch(`${API_BASE_URL}/api/website/leads/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(leadData),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create lead');
  }
  
  return response.json();
};

// Использование
createLead({
  name: 'Иван Иванов',
  phone: '+79991234567',
  email: 'ivan@example.com',
  city: 1,
  service: 2,
  message: 'Нужен шиномонтаж',
}).then(lead => console.log('Lead created:', lead));
```

### 4. Обработка ошибок
```javascript
const fetchWithErrorHandling = async (url) => {
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      // 404 - объект не найден или не активен
      if (response.status === 404) {
        console.error('Resource not found or inactive');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};
```

## ✅ Итоговая оценка

### Готовность к работе с фронтендом: **100%** ✅

**Что работает:**
- ✅ Все API эндпоинты доступны и работают
- ✅ CORS настроен корректно для разработки
- ✅ Сервер стабильно работает в Docker
- ✅ База данных настроена и наполнена тестовыми данными
- ✅ Swagger UI доступен для тестирования
- ✅ Создание заявок работает без аутентификации
- ✅ Фильтрация и пагинация работают корректно

**Нет блокирующих проблем для фронтенда!** 🎉

## 🔍 Дополнительная информация

- **Документация API:** `http://localhost:8000/api/docs/`
- **Спецификация OpenAPI:** Доступна в формате YAML по адресу `/api/schema/`
- **Админ-панель:** `http://localhost:8000/admin/` (требует авторизацию)
- **Логи:** Доступны через `docker-compose logs web`

---

**Последнее обновление:** 27 декабря 2025, 21:00 МСК

