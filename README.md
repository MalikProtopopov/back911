# 911 Corporate Website Backend

REST API для корпоративного сайта 911 на Django + DRF + PostgreSQL

## ✨ Особенности

- ✅ Django 5.0.3 + Django REST Framework
- ✅ PostgreSQL 15
- ✅ Poetry для управления зависимостями
- ✅ Docker + Docker Compose для dev и prod
- ✅ Автоматическая документация API (Swagger/ReDoc)
- ✅ Модели для городов, услуг, опций, преимуществ, метрик, контактов
- ✅ SEO-оптимизация для каждой страницы
- ✅ Система заявок с UTM метками

## 📁 Структура проекта

Проект организован по современным практикам для удобной поддержки:
- `docker/` - все Docker конфигурации
- `scripts/` - скрипты автоматизации (деплой, обновление)
- `config/` - шаблоны конфигурационных файлов
- `docs/` - документация (включая `docs/deployment/` для деплоя)

Подробнее см. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🚀 Быстрый старт (Dev)

### С Docker Compose (рекомендуется)

```bash
# 1. Клонируйте репозиторий
cd /Users/mak/Desktop/911_backend_website

# 2. Запустите проект
docker compose -f docker/docker-compose.dev.yml up -d

# 3. Применить миграции
docker compose -f docker/docker-compose.dev.yml exec web python manage.py migrate

# 4. Создать суперпользователя
docker compose -f docker/docker-compose.dev.yml exec web python manage.py createsuperuser

# 5. Загрузить начальные данные
docker compose -f docker/docker-compose.dev.yml exec web bash scripts/import_all_data.sh
```

**Примечание**: Этот скрипт импортирует ВСЕ данные из SQL дампа (82 города, услуги, опции, цены) и генерирует контент и SEO.

### Локально с Poetry

```bash
# 1. Установить зависимости
poetry install

# 2. Настроить окружение
cp .env.example .env
# Отредактируйте .env с вашими настройками

# 3. Запустить PostgreSQL (или использовать Docker)
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_DB=website_911_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:15-alpine

# 4. Применить миграции
poetry run python manage.py migrate

# 5. Создать суперпользователя
poetry run python manage.py createsuperuser

# 6. Загрузить данные
chmod +x scripts/import_all_data.sh
poetry run bash scripts/import_all_data.sh

# 7. Запустить сервер
poetry run python manage.py runserver
```

## 📦 Импорт данных из SQL дампа

Проект поддерживает полный импорт данных из SQL дампа основного приложения 911.

### Автоматический импорт (рекомендуется)

```bash
# В Docker
docker-compose -f docker-compose.dev.yml exec web bash scripts/import_all_data.sh

# Локально
chmod +x scripts/import_all_data.sh
poetry run bash scripts/import_all_data.sh
```

Этот скрипт импортирует:
- **82 города** из дампа с автоматической генерацией slug
- **4 услуги** (Шиномонтаж, Эвакуатор, Доставка топлива, Автовышка)
- **60+ опций** услуг с привязкой к городам
- **8 категорий техники** (Легковой, Грузовой, и т.д.)
- **Тысячи цен** для всех комбинаций город-услуга-опция
- **HTML контент** для всех страниц (шаблоны с подстановкой города)
- **SEO метаданные** по формулам для ~400+ страниц

### Ручной импорт (по шагам)

Если нужно импортировать данные поэтапно:

```bash
# 1. Импорт базовых данных
python manage.py import_cities              # 82 города
python manage.py import_services            # 4 услуги
python manage.py import_technic_categories  # 8 категорий техники
python manage.py import_options             # 60+ опций
python manage.py import_prices              # Тысячи цен

# 2. Загрузка статических данных
python manage.py loaddata \
    website_api/fixtures/initial_advantages.json \
    website_api/fixtures/initial_metrics.json \
    website_api/fixtures/initial_contacts.json \
    website_api/fixtures/initial_app_links.json

# 3. Генерация контента
python manage.py generate_content           # HTML для всех страниц

# 4. Генерация SEO
python manage.py generate_seo               # SEO метаданные
```

### Опции команд

Каждая команда поддерживает дополнительные опции:

```bash
# Указать путь к дампу (по умолчанию archive/911_last.sql)
python manage.py import_cities --dump-path=/path/to/dump.sql

# Регенерировать существующий контент
python manage.py generate_content --regenerate
python manage.py generate_seo --regenerate

# Размер батча для импорта цен (по умолчанию 1000)
python manage.py import_prices --batch-size=500
```

### Результат импорта

После выполнения всех команд в базе данных будет:

| Данные | Количество | Описание |
|--------|-----------|----------|
| Города | 82 | Все города присутствия из дампа |
| Услуги | 4 | Основные услуги платформы |
| Опции | 60+ | Опции для каждой услуги |
| Категории техники | 8 | Типы автомобилей и техники |
| Цены | ~2000+ | Цены для всех комбинаций |
| SEO метаданные | ~400+ | Главная + города + услуги + комбинации |
| HTML контент | ~400+ | Страницы с готовым контентом |

**🎉 Ваш сайт готов для продакшена с полной базой данных!**

## 📚 API Документация

После запуска проекта доступны интерактивные документации API:

- **Swagger UI**: http://localhost:8000/api/docs/ - интерактивная документация с возможностью тестирования запросов
- **ReDoc**: http://localhost:8000/api/redoc/ - альтернативная документация в стиле ReDoc
- **OpenAPI Schema**: http://localhost:8000/api/schema/ - схема API в формате OpenAPI 3.0 (JSON)
- **Django Admin**: http://localhost:8000/admin/ - административная панель Django

### Особенности API

- ✅ **Фильтрация по активности**: Все эндпоинты возвращают только активные объекты (is_active=True)
- ✅ **404 для неактивных**: Неактивные объекты возвращают 404 при запросе деталей
- ✅ **Limit/Offset пагинация**: `?limit=20&offset=0` для управления списками
  - `limit` - количество элементов (по умолчанию 20, максимум 100)
  - `offset` - смещение от начала (по умолчанию 0)
- ✅ **Поиск и фильтрация**: Поддержка query-параметров для фильтрации и поиска
- ✅ **SEO-оптимизация**: Каждая страница имеет свои SEO метаданные

## 🔗 API Endpoints

### Публичные эндпоинты

- `GET /api/website/cities/` - Список городов
- `GET /api/website/cities/{slug}/` - Детальная информация о городе
- `GET /api/website/services/` - Список услуг
- `GET /api/website/services/{slug}/` - Детальная информация об услуге
- `GET /api/website/cities/{city_slug}/services/{service_slug}/` - Услуга в конкретном городе
- `GET /api/website/options/` - Список опций (с фильтрацией по городу и услуге)
- `GET /api/website/advantages/` - Преимущества платформы
- `GET /api/website/metrics/` - Бизнес-метрики
- `GET /api/website/contacts/` - Контактная информация
- `GET /api/website/app-links/` - Ссылки на мобильные приложения
- `GET /api/website/seo-meta/` - SEO метаданные для страниц
- `POST /api/website/leads/` - Создание заявки с сайта

## 🧪 Тестирование

```bash
# С Docker
docker compose -f docker/docker-compose.dev.yml exec web pytest

# Локально
poetry run pytest
poetry run pytest --cov=website_api
```

## 🏗️ Структура проекта

```
911_backend_website/
├── website_project/          # Django project settings
│   ├── settings/
│   │   ├── base.py          # Базовые настройки
│   │   ├── dev.py           # Dev настройки
│   │   └── prod.py          # Production настройки
│   ├── urls.py
│   └── wsgi.py
├── website_api/             # Django app
│   ├── models/              # Модели данных
│   ├── serializers/         # DRF сериализаторы
│   ├── views/               # API views
│   ├── admin/               # Django admin
│   ├── fixtures/            # Начальные данные
│   └── tests/               # Тесты
├── docs/                    # Документация
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.dev.yml   # Dev окружение
│   ├── docker-compose.prod.yml  # Production окружение
│   ├── nginx.conf
│   └── entrypoint.sh
├── Dockerfile              # Docker образ
├── pyproject.toml          # Poetry зависимости
└── README.md
```

## 🌐 Production

```bash
# 1. Создать .env.prod с production настройками
cp .env .env.prod
# Отредактировать .env.prod

# 2. Запустить (или используйте скрипт: bash scripts/deploy.sh)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d

# 3. Применить миграции (или используйте AUTO_MIGRATE=true в .env.prod)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 4. Статика собирается автоматически через entrypoint.sh
# Но можно собрать вручную:
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# 5. Создать суперпользователя
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 🔧 Управление

```bash
# Просмотр логов
docker compose -f docker/docker-compose.dev.yml logs -f web

# Остановить проект
docker compose -f docker/docker-compose.dev.yml down

# Остановить и удалить volumes
docker compose -f docker/docker-compose.dev.yml down -v

# Пересобрать образы
docker compose -f docker/docker-compose.dev.yml build --no-cache

# Выполнить команду Django
docker compose -f docker/docker-compose.dev.yml exec web python manage.py <command>
```

## 📝 Переменные окружения

Создайте файл `.env` с следующими переменными:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=website_911_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 👥 Credentials (Dev)

- **Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`

## 📌 Что НЕ включено

Для упрощения архитектуры убраны:
- ❌ Celery (фоновые задачи)
- ❌ Redis (если не нужен для кеширования)
- ❌ Elasticsearch (поиск)
- ❌ WebSockets (real-time)

Если понадобятся - можно добавить позже.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License
# back911
# back911
# back911
