"""
Django settings for website_project project.
Base settings shared across all environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third party apps
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # "django_ckeditor_5",  # Temporarily disabled due to installation issues
    
    # Local apps
    "website_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS должен быть перед CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "website_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "website_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "website_911_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "website_api.pagination.OptionalLimitOffsetPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "911 Corporate Website API",
    "DESCRIPTION": """
REST API для корпоративного сайта 911

## Основные возможности

- **Города**: Получение списка городов присутствия и детальной информации
- **Услуги**: Информация об услугах (эвакуатор, шиномонтаж, техпомощь и др.)
- **Опции и цены**: Опции услуг с ценами по городам
- **SEO**: Метаданные для всех страниц сайта
- **Статический контент**: Преимущества, метрики, контакты, ссылки на приложения
- **Заявки**: Прием заявок с корпоративного сайта

## Фильтрация по активности

Все основные эндпоинты (города, услуги, опции) возвращают **только активные объекты** (is_active=True).
Неактивные объекты не отображаются в списках и возвращают **404** при запросе деталей.

## Пагинация

API использует **limit/offset пагинацию**:
- Всегда возвращает объект пагинации с полями: `count`, `next`, `previous`, `results`
- Если параметры `limit` или `offset` **не указаны** - возвращаются **все записи** в поле `results`
- Если параметры указаны - применяется пагинация:
  - `?limit=20` - количество элементов на странице (по умолчанию 20, максимум 100)
  - `?offset=0` - смещение от начала списка (по умолчанию 0)

**Примеры:**
- `GET /api/cities/` - все города в формате `{count: N, results: [...], next: null, previous: null}`
- `GET /api/cities/?limit=10` - первые 10 городов с пагинацией
- `GET /api/cities/?limit=50&offset=100` - города с 101 по 150

## Документация

- **Swagger UI**: `/api/docs/` - интерактивная документация с возможностью тестирования
- **ReDoc**: `/api/redoc/` - альтернативная документация в формате ReDoc
- **OpenAPI Schema**: `/api/schema/` - схема в формате OpenAPI 3.0

## Поддержка

Email: support@911.ru
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "CONTACT": {
        "name": "911 Support Team",
        "email": "support@911.ru",
    },
    "LICENSE": {
        "name": "Proprietary",
    },
    # Группировка эндпоинтов по тегам
    "TAGS": [
        {"name": "Города", "description": "Операции с городами присутствия"},
        {"name": "Услуги", "description": "Информация об услугах"},
        {"name": "Опции услуг", "description": "Опции услуг и их цены по городам"},
        {"name": "Город + Услуга", "description": "Комбинированная информация об услуге в конкретном городе"},
        {"name": "SEO", "description": "SEO метаданные для страниц"},
        {"name": "Статический контент", "description": "Преимущества, метрики, контакты, ссылки на приложения"},
        {"name": "Заявки", "description": "Прием и управление заявками с сайта"},
    ],
    # Схема сортировки эндпоинтов
    "ENUM_NAME_OVERRIDES": {
        "TargetAudienceEnum": "website_api.models.advantage.Advantage.TARGET_AUDIENCE_CHOICES",
        "MetricTypeEnum": "website_api.models.metric.Metric.METRIC_TYPE_CHOICES",
        "ContactTypeEnum": "website_api.models.contact.Contact.CONTACT_TYPE_CHOICES",
        "PlatformEnum": "website_api.models.app_link.AppLink.PLATFORM_CHOICES",
        "AppTypeEnum": "website_api.models.app_link.AppLink.APP_TYPE_CHOICES",
        "PageTypeEnum": "website_api.models.seo_meta.SeoMeta.PAGE_TYPE_CHOICES",
        "LeadStatusEnum": "website_api.models.lead.Lead.STATUS_CHOICES",
    },
    # Дополнительные настройки
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "filter": True,
        "tryItOutEnabled": True,
        "supportedSubmitMethods": ["get", "post", "put", "patch", "delete"],
        "validatorUrl": None,  # Отключаем валидатор, чтобы избежать CORS проблем
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "expandResponses": "200,201",
    },
}


# Cache settings (local memory cache for development)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


# CKEditor 5 configuration
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'bulletedList', 'numberedList', '|',
            'blockQuote', 'insertTable', '|',
            'undo', 'redo', '|',
            'sourceEditing'
        ],
        'height': 400,
        'width': '100%',
    },
    'extends': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', 'code', '|',
            'fontSize', 'fontColor', 'fontBackgroundColor', '|',
            'link', 'bulletedList', 'numberedList', 'todoList', '|',
            'blockQuote', 'insertTable', 'imageUpload', 'mediaEmbed', '|',
            'horizontalLine', 'specialCharacters', '|',
            'alignment', 'indent', 'outdent', '|',
            'undo', 'redo', '|',
            'sourceEditing'
        ],
        'height': 600,
        'width': '100%',
    }
}

