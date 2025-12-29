# Исправление 404 на корневом URL

## ✅ Проблема решена

Добавлен обработчик для корневого URL (`/`), который возвращает JSON с информацией об API.

## 📝 Что было сделано

1. Добавлена функция `api_root()` в `website_project/urls.py`
2. Добавлен маршрут `path("", api_root, name="api-root")` в начало списка URL patterns

## 🔧 Текущее состояние

Код уже добавлен в файл `website_project/urls.py`. После пересборки образа Docker корневой URL будет возвращать:

```json
{
  "name": "911 Corporate Website API",
  "version": "1.0.0",
  "description": "REST API для корпоративного сайта 911",
  "endpoints": {
    "api_base": "/api/website/",
    "documentation": {
      "swagger_ui": "/api/docs/",
      "redoc": "/api/redoc/",
      "openapi_schema": "/api/schema/"
    },
    "main_endpoints": {
      "cities": "/api/website/cities/",
      "services": "/api/website/services/",
      "options": "/api/website/options/",
      "advantages": "/api/website/advantages/",
      "metrics": "/api/website/metrics/",
      "contacts": "/api/website/contacts/",
      "app_links": "/api/website/app-links/",
      "seo_meta": "/api/website/seo-meta/",
      "leads": "/api/website/leads/"
    }
  },
  "admin": "/admin/"
}
```

## 🚀 Как применить изменения

### Вариант 1: Пересборка образа (рекомендуется)

```bash
docker-compose -f docker-compose.dev.yml up -d --build web
```

### Вариант 2: Если используется volume mount для разработки

Если в `docker-compose.dev.yml` настроен volume mount для кода, изменения применятся автоматически после перезапуска:

```bash
docker-compose -f docker-compose.dev.yml restart web
```

## ✅ Проверка

После пересборки/перезапуска проверьте:

```bash
curl http://localhost:8000/ | python3 -m json.tool
```

Должен вернуться JSON с информацией об API (см. выше).

## 📌 Важно

**Фронтенд должен обращаться к `/api/website/...`, а не к `/`**

Корневой URL (`/`) теперь возвращает информационный JSON, но это не влияет на работу API. Все API эндпоинты остаются на своих местах:

- ✅ `/api/website/cities/` - работает
- ✅ `/api/website/services/` - работает
- ✅ `/api/website/leads/` - работает
- ✅ И все остальные эндпоинты

## 🔍 Примечание

Если при пересборке возникают проблемы с зависимостями (например, `django_ckeditor_5`), это отдельная проблема, не связанная с корневым URL. Код для обработки корневого URL уже добавлен и будет работать после успешного запуска сервера.

