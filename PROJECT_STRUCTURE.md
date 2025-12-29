# 📁 Структура проекта

Этот документ описывает организацию файлов и папок проекта для удобной поддержки и разработки.

## 🗂️ Основная структура

```
911_backend_website/
├── docker/                    # Docker конфигурация
│   ├── Dockerfile            # Docker образ для приложения
│   ├── docker-compose.prod.yml  # Production конфигурация
│   ├── docker-compose.dev.yml  # Development конфигурация
│   ├── nginx.conf            # Конфигурация Nginx
│   └── entrypoint.sh         # Скрипт запуска контейнера
│
├── scripts/                   # Скрипты для автоматизации
│   ├── deploy.sh             # Скрипт деплоя на production
│   ├── update.sh             # Скрипт обновления проекта
│   ├── import_all_data.sh    # Импорт данных
│   └── load_all_data.sh      # Загрузка данных
│
├── config/                    # Конфигурационные шаблоны
│   └── env.prod.template     # Шаблон .env.prod файла
│
├── docs/                      # Документация
│   ├── deployment/           # Документация по деплою
│   │   ├── PRODUCTION_DEPLOYMENT.md
│   │   ├── QUICK_DEPLOY.md
│   │   ├── SERVER_SETUP.md
│   │   └── ...
│   ├── api/                  # API документация (если есть)
│   └── ...                   # Другая документация
│
├── website_project/          # Основной Django проект
│   ├── settings/            # Настройки (dev, prod, base)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── website_api/              # Django приложение API
│   ├── models/              # Модели данных
│   ├── views/               # Представления (views)
│   ├── serializers/         # Сериализаторы DRF
│   ├── management/          # Management команды
│   ├── tests/               # Тесты
│   └── fixtures/            # Фикстуры для тестов
│
├── static/                   # Статические файлы (исходники)
├── staticfiles/              # Собранные статические файлы (gitignore)
├── media/                    # Медиа файлы (gitignore)
│
├── manage.py                 # Django management скрипт
├── pyproject.toml            # Poetry конфигурация
├── poetry.lock              # Poetry lock файл
├── pytest.ini               # Конфигурация pytest
├── conftest.py              # Pytest фикстуры
│
├── .env.prod                # Production переменные окружения (gitignore)
├── .gitignore               # Git ignore правила
│
└── README.md                # Основная документация проекта
```

## 📂 Описание директорий

### `docker/`
Все файлы, связанные с Docker:
- **Dockerfile** - определение образа приложения
- **docker-compose.prod.yml** - production окружение
- **docker-compose.dev.yml** - development окружение
- **nginx.conf** - конфигурация веб-сервера
- **entrypoint.sh** - скрипт инициализации контейнера

### `scripts/`
Скрипты для автоматизации задач:
- **deploy.sh** - полный деплой на production
- **update.sh** - обновление существующего деплоя
- **import_all_data.sh** - импорт данных в БД
- **load_all_data.sh** - загрузка данных

### `config/`
Шаблоны конфигурационных файлов:
- **env.prod.template** - шаблон для создания `.env.prod`

### `docs/`
Вся документация проекта:
- **deployment/** - документация по развертыванию
- **api/** - API документация
- Остальная техническая и бизнес-документация

### `website_project/`
Основной Django проект:
- **settings/** - настройки для разных окружений
- **urls.py** - главный URL конфиг
- **wsgi.py** / **asgi.py** - точки входа для WSGI/ASGI

### `website_api/`
Django приложение с API:
- **models/** - модели данных
- **views/** - представления (API endpoints)
- **serializers/** - сериализаторы DRF
- **management/commands/** - кастомные команды Django
- **tests/** - тесты приложения
- **fixtures/** - тестовые данные

## 🚀 Использование

### Запуск скриптов

Все скрипты запускаются из корня проекта:

```bash
# Деплой
bash scripts/deploy.sh

# Обновление
bash scripts/update.sh
```

### Docker команды

```bash
# Production
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d

# Development
docker compose -f docker/docker-compose.dev.yml up -d
```

## 📝 Принципы организации

1. **Разделение по назначению** - файлы группируются по их функции
2. **Чистый корень** - в корне только самые важные файлы
3. **Логическая группировка** - связанные файлы в одной папке
4. **Стандартные практики** - структура следует общепринятым конвенциям Django/Docker

## 🔄 Миграция со старой структуры

Если вы обновляете проект со старой структуры, убедитесь что:
- Все пути в скриптах обновлены
- Docker compose файлы указывают на правильные пути
- Документация обновлена с новыми путями

