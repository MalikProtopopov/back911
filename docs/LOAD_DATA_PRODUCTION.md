# Загрузка данных на Production сервере (через fixtures)

## 🎯 Какой скрипт использовать

В проекте есть два способа заполнения базы:

1. **`scripts/load_all_data.sh`** - использует fixtures (JSON файлы) ✅ **Этот скрипт для вас!**
2. `scripts/import_all_data.sh` - использует SQL дамп (не нужен)

## 🚀 Быстрый запуск

### На production сервере:

```bash
# 1. Подключиться к серверу
ssh root@45.144.221.92
cd ~/back911

# 2. Убедиться, что контейнеры запущены
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml ps

# 3. Применить миграции (если еще не применены)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 4. Запустить скрипт загрузки данных
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web bash scripts/load_all_data.sh
```

## 📋 Что делает скрипт `load_all_data.sh`

### Шаг 1: Загрузка базовых данных из fixtures
- ✅ 82 города (`cities.json`)
- ✅ 4 услуги (`services.json`)
- ✅ Категории техники (`technic_categories.json`)
- ✅ Опции услуг (`options.json`)
- ✅ Примеры цен (`option_prices.json`)

### Шаг 2: Загрузка статического контента
- ✅ Преимущества (`initial_advantages.json`)
- ✅ Метрики (`initial_metrics.json`)
- ✅ Контакты (`initial_contacts.json`)
- ✅ Ссылки на приложения (`initial_app_links.json`)

### Шаг 3: Генерация динамического контента
- ✅ HTML контент для городов
- ✅ HTML контент для услуг

### Шаг 4: Генерация SEO метаданных
- ✅ SEO для главной страницы
- ✅ SEO для страниц городов
- ✅ SEO для страниц услуг
- ✅ SEO для страниц город-услуга

## 🔧 Альтернативный способ: Поэтапная загрузка

Если нужно загружать данные по шагам:

```bash
cd ~/back911

# 1. Базовые данные
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata website_api/fixtures/cities.json
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata website_api/fixtures/services.json
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata website_api/fixtures/technic_categories.json
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata website_api/fixtures/options.json
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata website_api/fixtures/option_prices.json

# 2. Статический контент
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata \
    website_api/fixtures/initial_advantages.json \
    website_api/fixtures/initial_metrics.json \
    website_api/fixtures/initial_contacts.json \
    website_api/fixtures/initial_app_links.json

# 3. Генерация контента
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content --cities
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content --services

# 4. Генерация SEO
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --home
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --cities
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --services
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --city-services
```

## ✅ Проверка результата

После загрузки проверьте статистику:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "
from website_api.models import City, Service, Option, OptionPrice, ServiceContent, SeoMeta
print('Cities:', City.objects.count())
print('Services:', Service.objects.count())
print('Options:', Option.objects.count())
print('Prices:', OptionPrice.objects.count())
print('Service Content:', ServiceContent.objects.count())
print('SEO Metadata:', SeoMeta.objects.count())
"
```

**Ожидаемые результаты:**
- Cities: 82
- Services: 4
- Options: 50+
- Prices: примеры для основных городов
- Service Content: сотни записей
- SEO Metadata: сотни записей

## 🐛 Решение проблем

### Проблема 1: Fixtures не найдены

**Ошибка:**
```
No such file or directory: website_api/fixtures/cities.json
```

**Решение:**
1. Убедитесь, что fixtures есть в репозитории:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web ls -la website_api/fixtures/
   ```

2. Если файлов нет, убедитесь, что они есть в репозитории и пересоберите контейнер:
   ```bash
   git pull
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml build web
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
   ```

### Проблема 2: Ошибки при загрузке fixtures

**Ошибка:**
```
IntegrityError: duplicate key value violates unique constraint
```

**Решение:**
Данные уже загружены. Если нужно перезагрузить:
1. Очистите базу (осторожно!):
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py flush --no-input
   ```

2. Или используйте флаг `--update` (если поддерживается):
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata --update website_api/fixtures/cities.json
   ```

### Проблема 3: Ошибки базы данных

**Решение:**
1. Проверьте подключение к базе:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py dbshell
   ```

2. Убедитесь, что миграции применены:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate
   ```

### Проблема 4: Ошибки при генерации контента/SEO

**Решение:**
1. Проверьте логи:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs web | tail -50
   ```

2. Попробуйте регенерировать:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content --regenerate
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --regenerate
   ```

## 📝 Пример полного процесса

```bash
# 1. Подключиться к серверу
ssh root@45.144.221.92

# 2. Перейти в директорию проекта
cd ~/back911

# 3. Убедиться, что контейнеры запущены
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml ps

# 4. Применить миграции
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 5. Запустить загрузку данных
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web bash scripts/load_all_data.sh

# 6. Проверить результат
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "
from website_api.models import City, Service, Option
print('Cities:', City.objects.count())
print('Services:', Service.objects.count())
print('Options:', Option.objects.count())
"
```

## ⚠️ Важные замечания

1. **Резервная копия:** Перед загрузкой данных рекомендуется сделать резервную копию базы:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec db pg_dump -U postgres website_911_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Время выполнения:** Загрузка данных занимает 2-5 минут.

3. **Повторная загрузка:** Если запустить скрипт повторно, могут быть ошибки дублирования. Используйте `--update` или очистите базу перед повторной загрузкой.

4. **Мониторинг:** Следите за логами во время загрузки:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs -f web
   ```

---

**Готово!** После успешной загрузки ваш сайт будет заполнен данными из fixtures.

