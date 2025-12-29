FROM python:3.11-slim AS builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry==1.7.1

# Настройка Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Копирование файлов зависимостей
# poetry.lock может отсутствовать в репозитории, поэтому копируем опционально
COPY pyproject.toml ./
COPY poetry.lock* ./

# Установка зависимостей (без dev зависимостей для production)
# Если poetry.lock отсутствует, poetry создаст его автоматически
RUN if [ -f poetry.lock ]; then \
        poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR; \
    else \
        poetry lock --no-update && \
        poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR; \
    fi

# Финальный образ
FROM python:3.11-slim

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd -m -u 1000 django && mkdir -p /app && chown -R django:django /app

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder --chown=django:django /app/.venv /app/.venv

# Установка PATH для виртуального окружения ДО переключения на пользователя
ENV PATH="/app/.venv/bin:$PATH"

# Копирование кода приложения
COPY --chown=django:django . .

# Создание необходимых директорий
RUN mkdir -p /app/static /app/media /app/logs && \
    chown -R django:django /app/static /app/media /app/logs

# Установка прав на выполнение для entrypoint скрипта (копируется через COPY . . выше)
RUN chmod +x /app/entrypoint.sh

# Переключение на пользователя django
USER django

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/website/metrics/')" || exit 1

# Entrypoint скрипт будет автоматически собирать статику перед запуском
ENTRYPOINT ["/app/entrypoint.sh"]
