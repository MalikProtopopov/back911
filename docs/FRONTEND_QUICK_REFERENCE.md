# Быстрая справка для фронтенда

## ⚠️ Важно: Фронтенд и бекенд на разных серверах

- **Фронтенд:** `http://89.169.1.53/` (ваш сервер)
- **Бекенд (API):** `http://45.144.221.92/` (другой сервер)

**Все запросы к API должны идти на бекенд-сервер!**

## 🔗 Базовые URL

```
API Base URL: http://45.144.221.92/api/website/
Документация: http://45.144.221.92/api/docs/
```

**❌ НЕ используйте:** `http://89.169.1.53/api/website/` (это адрес фронтенда, бекенда там нет!)

## 📋 Основные Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/website/cities/` | GET | Список городов |
| `/api/website/cities/{slug}/` | GET | Детали города |
| `/api/website/services/` | GET | Список услуг |
| `/api/website/services/{slug}/` | GET | Детали услуги |
| `/api/website/cities/{city_slug}/services/{service_slug}/` | GET | Услуга в городе |
| `/api/website/options/` | GET | Опции услуг |
| `/api/website/advantages/` | GET | Преимущества |
| `/api/website/metrics/` | GET | Метрики платформы |
| `/api/website/contacts/` | GET | Контакты |
| `/api/website/app-links/` | GET | Ссылки на приложения |
| `/api/website/seo-meta/` | GET | SEO метаданные |
| `/api/website/leads/` | POST | Создать заявку |

## 📝 Создание заявки (POST /api/website/leads/)

```json
{
  "name": "Иван Иванов",        // Обязательно
  "phone": "+79991234567",      // Обязательно
  "email": "ivan@example.com",  // Опционально
  "city": 1,                    // Опционально (ID)
  "service": 2,                // Опционально (ID)
  "message": "Текст заявки",   // Опционально
  "source_page": "/moskva/shinomontazh/",  // Опционально
  "utm_source": "google",      // Опционально
  "utm_medium": "cpc",         // Опционально
  "utm_campaign": "summer2024" // Опционально
}
```

## 🔧 Пример кода (JavaScript)

```javascript
// ⚠️ ВАЖНО: Используйте URL бекенда (45.144.221.92), а не фронтенда (89.169.1.53)!
const API_BASE = 'http://45.144.221.92/api/website';

// Получить города
fetch(`${API_BASE}/cities/`)
  .then(res => res.json())
  .then(data => console.log(data.results));

// Создать заявку
fetch(`${API_BASE}/leads/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Иван Иванов',
    phone: '+79991234567',
    city: 1,
    service: 2
  })
})
  .then(res => res.json())
  .then(data => console.log('Lead created:', data));
```

## ⚠️ Важно

1. **CORS:** Убедитесь, что ваш URL добавлен в `CORS_ALLOWED_ORIGINS` на бекенде
2. **Порт:** Если фронт не на стандартном порту, укажите порт в CORS настройках
3. **Валидация:** Телефон - 10-12 цифр, Имя - минимум 2 символа

## 📚 Полная документация

См. [FRONTEND_DEPLOYMENT_GUIDE.md](./FRONTEND_DEPLOYMENT_GUIDE.md) для подробной информации.

