import os
from datetime import timedelta

from pathlib import Path

from celery.schedules import crontab
from corsheaders.defaults import default_headers

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["*"]

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG")

AUTH_USER_MODEL = "users.CustomUser"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

redis_port = "redis://redis:6379"

if DEBUG and os.environ.get("REDIS_PORT_CONFIG"):
    redis_port = os.environ.get("REDIS_PORT_CONFIG")

MY_APPS = [
    "users",
    "src",
    "websocket",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "channels",
    "django.contrib.postgres",
    "django_filters",
    "django_elasticsearch_dsl",
    "django_celery_beat",
] + MY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
    ]

CORS_ALLOW_HEADERS = list(default_headers) + ["Set-Cookie"]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_ROOT / "dist",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [redis_port + "/1"],
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication",
    ),
    "DATETIME_FORMAT": "%d.%m.%Y %H:%M:%S",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "src.services.exceptions.handle_django_validation_error",
    "COERCE_DECIMAL_TO_STRING": False,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "911 API",
    "DESCRIPTION": "API SCHEMA",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": "http://elastic_node:9200",
        "http_auth": ("test_user", "StrongPassw0rd1"),
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": (
        "Bearer",
        "JWT",
    ),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

CSRF_USE_SESSIONS = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

CSRF_TRUSTED_ORIGINS = [os.environ.get("CSRF_TRUSTED")]

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("POSTGRES_ENGINE"),
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}


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

CELERY_BROKER_URL = redis_port + "/0"
CELERY_RESULT_BACKEND = redis_port
CELERY_IMPORTS = []
CELERY_TIMEZONE = "UTC"
CELERY_ACCEPT_CONTENT = ["pickle", "json"]
CELERY_BEAT_SCHEDULE = {
    "update-partners-es-every-5-min": {
        "task": "src.tasks.partner_tasks.update_partner_documents",
        "schedule": crontab(minute="*/2"),
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_port,
        "OPTIONS": {
            "db": "1",
        },
    }
}

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_TZ = True

MEDIA_URL = "/media/"

if media_path := os.environ.get("MEDIA_PATH"):
    MEDIA_HDD = Path(media_path)
    MEDIA_ROOT = os.path.join(MEDIA_HDD, "media")
else:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "assets"),
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FCMTOKEN_PATH = os.path.join(
    PROJECT_ROOT, "fcmtoken", "mobile-app-3ccf1-firebase-adminsdk-59l7p-da3f4bde1c.json"
)

SMS_RU_URL = os.environ.get("SMS_RU_URL")
SMS_RU_TOKEN = os.environ.get("SMS_RU_TOKEN")

TINKOFF_TERMINAL_KEY = os.environ.get("TINKOFF_TERMINAL_KEY")
TINKOFF_TOKEN = os.environ.get("TINKOFF_TOKEN")

CLOUD_PAYMENTS_USERNAME = os.environ.get("CLOUD_PAYMENTS_USERNAME")
CLOUD_PAYMENTS_PASSWORD = os.environ.get("CLOUD_PAYMENTS_PASSWORD")
