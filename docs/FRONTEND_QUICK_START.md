# 🚀 Быстрый старт для фронтенд-разработчика

## ✅ Статус бекенда

**Бекенд работает и готов к интеграции!**

- 🟢 Сервер запущен: `http://localhost:8000`
- 🟢 CORS настроен корректно
- 🟢 Все API эндпоинты доступны
- 🟢 Тестовые данные загружены

## 🔗 Важные ссылки

- **API базовый URL:** `http://localhost:8000/api/website/`
- **Swagger документация:** http://localhost:8000/api/docs/
- **ReDoc документация:** http://localhost:8000/api/redoc/
- **OpenAPI схема:** http://localhost:8000/api/schema/

## 🎯 Основные эндпоинты

### Получение данных (GET)

```javascript
const API_URL = 'http://localhost:8000/api/website';

// Список городов
fetch(`${API_URL}/cities/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Список услуг
fetch(`${API_URL}/services/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Детали услуги по slug
fetch(`${API_URL}/services/shinomontazh/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Услуга в конкретном городе
fetch(`${API_URL}/cities/moskva/services/shinomontazh/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Метрики
fetch(`${API_URL}/metrics/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Преимущества
fetch(`${API_URL}/advantages/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Контакты
fetch(`${API_URL}/contacts/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Ссылки на приложения (iOS для клиентов)
fetch(`${API_URL}/app-links/?platform=ios&app_type=client`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### Создание заявки (POST)

```javascript
const createLead = async (leadData) => {
  const response = await fetch('http://localhost:8000/api/website/leads/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(leadData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(JSON.stringify(error));
  }
  
  return response.json();
};

// Минимальный пример
createLead({
  name: 'Иван Иванов',
  phone: '+79991234567',
}).then(lead => console.log('Заявка создана:', lead));

// Полный пример с UTM
createLead({
  name: 'Иван Иванов',
  phone: '+79991234567',
  email: 'ivan@example.com',
  city: 1,
  service: 2,
  message: 'Нужен шиномонтаж завтра утром',
  source_page: window.location.pathname,
  utm_source: 'google',
  utm_medium: 'cpc',
  utm_campaign: 'shinomontazh_moskva',
}).then(lead => console.log('Заявка создана:', lead));
```

## 📋 React Hook пример

```javascript
import { useState, useEffect } from 'react';

// Хук для загрузки данных
function useAPI(endpoint) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/website/${endpoint}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [endpoint]);

  return { data, loading, error };
}

// Использование
function ServicesList() {
  const { data: services, loading, error } = useAPI('services/');

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;

  return (
    <div>
      {services.map(service => (
        <div key={service.id}>
          <h3>{service.title}</h3>
          <p>{service.short_description}</p>
        </div>
      ))}
    </div>
  );
}
```

## 🎨 Примеры ответов API

### Список городов
```json
[
  {
    "id": 1,
    "title": "Москва",
    "slug": "moskva",
    "latitude": "55.755826",
    "longitude": "37.617300",
    "display_order": 1
  },
  {
    "id": 2,
    "title": "Санкт-Петербург",
    "slug": "sankt-peterburg",
    "latitude": "59.934280",
    "longitude": "30.335099",
    "display_order": 2
  }
]
```

### Список услуг
```json
[
  {
    "id": 1,
    "title": "Выездной шиномонтаж",
    "slug": "shinomontazh",
    "icon_url": "/static/icons/shinomontazh.svg",
    "options_count": 56
  },
  {
    "id": 3,
    "title": "Эвакуатор / манипулятор",
    "slug": "evakuator",
    "icon_url": "/static/icons/evakuator.svg",
    "options_count": 2
  }
]
```

### Детали услуги
```json
{
  "id": 1,
  "title": "Выездной шиномонтаж",
  "slug": "shinomontazh",
  "short_description": "Мобильный шиномонтаж с выездом",
  "full_description": "<p>Полное описание услуги...</p>",
  "icon_url": "/static/icons/shinomontazh.svg",
  "display_order": 1,
  "options": [
    {
      "id": 1,
      "title": "R13",
      "slug": "r13",
      "description": "Радиус 13",
      "unit": "шт",
      "prices": [
        {
          "city_id": 1,
          "city_title": "Москва",
          "price": "300.00",
          "currency": "RUB"
        }
      ]
    }
  ]
}
```

### Создание заявки (ответ)
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "city": 1,
  "city_title": "Москва",
  "service": 2,
  "service_title": "Выездной шиномонтаж",
  "message": "Нужен шиномонтаж завтра утром",
  "source_page": "/moskva/shinomontazh/",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "shinomontazh_moskva",
  "status": "new",
  "status_display": "Новая",
  "created_at": "2025-12-27T18:06:01.811938+03:00",
  "processed_at": null
}
```

## 🔍 Фильтры и параметры

### Пагинация (опциональная)
```javascript
// Все записи (без пагинации)
fetch('http://localhost:8000/api/website/cities/')

// Первые 10 записей
fetch('http://localhost:8000/api/website/cities/?limit=10')

// Следующие 10 записей
fetch('http://localhost:8000/api/website/cities/?limit=10&offset=10')
```

### Фильтрация
```javascript
// Преимущества для клиентов
fetch('http://localhost:8000/api/website/advantages/?target_audience=client')

// Метрики платформы
fetch('http://localhost:8000/api/website/metrics/?metric_type=platform')

// Телефоны контактов
fetch('http://localhost:8000/api/website/contacts/?contact_type=phone')

// iOS приложение для клиентов
fetch('http://localhost:8000/api/website/app-links/?platform=ios&app_type=client')

// SEO для страницы города
fetch('http://localhost:8000/api/website/seo-meta/?page_type=city&city=1')
```

### Поиск
```javascript
// Поиск города по названию
fetch('http://localhost:8000/api/website/cities/?search=Москва')

// Поиск услуги
fetch('http://localhost:8000/api/website/services/?search=шиномонтаж')
```

## ⚠️ Обработка ошибок

### 404 - Не найдено
Объект не существует или неактивен (is_active=False)

```javascript
fetch('http://localhost:8000/api/website/services/neverexist/')
  .then(res => {
    if (res.status === 404) {
      console.log('Услуга не найдена или неактивна');
    }
    return res.json();
  });
```

### 400 - Ошибка валидации
```javascript
const createLead = async (data) => {
  try {
    const response = await fetch('http://localhost:8000/api/website/leads/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Validation errors:', error);
      // Пример ошибки:
      // { "phone": ["Введите правильное значение."] }
      throw error;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating lead:', error);
    throw error;
  }
};
```

## 🧪 Быстрые тесты

### В браузере (Console)
```javascript
// Тест 1: Получить города
fetch('http://localhost:8000/api/website/cities/')
  .then(r => r.json())
  .then(console.log);

// Тест 2: Получить услуги
fetch('http://localhost:8000/api/website/services/')
  .then(r => r.json())
  .then(console.log);

// Тест 3: Создать тестовую заявку
fetch('http://localhost:8000/api/website/leads/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Тест',
    phone: '+79991234567',
  }),
})
  .then(r => r.json())
  .then(console.log);
```

### В терминале (curl)
```bash
# Города
curl http://localhost:8000/api/website/cities/

# Услуги
curl http://localhost:8000/api/website/services/

# Создать заявку
curl -X POST http://localhost:8000/api/website/leads/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Тест","phone":"+79991234567"}'
```

## 🔒 Аутентификация

### Большинство эндпоинтов доступны БЕЗ аутентификации:
- ✅ Города
- ✅ Услуги
- ✅ Опции
- ✅ Преимущества
- ✅ Метрики
- ✅ Контакты
- ✅ Ссылки на приложения
- ✅ SEO метаданные
- ✅ **Создание заявки** (POST /leads/)

### Требуют аутентификацию (только для админов):
- 🔒 Просмотр списка заявок (GET /leads/)
- 🔒 Просмотр деталей заявки (GET /leads/{id}/)

## 📱 Environment Variables

Рекомендуется использовать переменные окружения:

```env
# .env.local (для React)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000

# .env.production
REACT_APP_API_URL=https://api.example.com
REACT_APP_API_TIMEOUT=10000
```

```javascript
// api.js
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_TIMEOUT = process.env.REACT_APP_API_TIMEOUT || 10000;
```

## 🐛 Отладка

### Проверка CORS
```javascript
// Должен вернуть заголовки Access-Control-*
fetch('http://localhost:8000/api/website/cities/', {
  headers: { 'Origin': 'http://localhost:3000' }
})
  .then(res => {
    console.log('CORS headers:', {
      'access-control-allow-origin': res.headers.get('access-control-allow-origin'),
      'access-control-allow-credentials': res.headers.get('access-control-allow-credentials'),
    });
    return res.json();
  })
  .then(console.log);
```

### Логи сервера
```bash
# Просмотр логов в реальном времени
docker-compose -f docker-compose.dev.yml logs web -f

# Последние 100 строк
docker-compose -f docker-compose.dev.yml logs web --tail=100
```

## ✅ Чек-лист готовности

- [x] Бекенд запущен и работает
- [x] CORS настроен и разрешает запросы с фронтенда
- [x] Все основные эндпоинты доступны
- [x] API возвращает валидный JSON
- [x] Создание заявок работает
- [x] Тестовые данные загружены
- [x] Swagger документация доступна
- [x] Нет блокирующих ошибок

## 🎉 Готово к интеграции!

Бекенд полностью готов к работе. Никаких ограничений или блокировок нет.

**Все запросы с фронтенда будут обработаны успешно!** ✅

---

**Дополнительная документация:**
- [Полный отчет о статусе API](./API_STATUS_REPORT.md)
- [Swagger UI](http://localhost:8000/api/docs/)
- [ReDoc](http://localhost:8000/api/redoc/)

