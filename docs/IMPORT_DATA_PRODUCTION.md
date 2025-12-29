# Импорт данных на Production сервере

## 📋 Подготовка

### 1. Убедитесь, что SQL дамп доступен

Скрипт импорта ожидает SQL дамп в папке `archive/911_last.sql` внутри контейнера.

**Вариант A: Если дамп уже в репозитории**

Если файл `archive/911_last.sql` уже есть в репозитории, он будет скопирован в контейнер при сборке.

**Вариант B: Если нужно загрузить дамп на сервер**

```bash
# На сервере бекенда
cd ~/back911

# Создать папку archive, если её нет
mkdir -p archive

# Загрузить дамп (через scp с локального компьютера)
# scp /path/to/911_last.sql root@45.144.221.92:~/back911/archive/

# Или скачать с другого сервера
# wget https://example.com/911_last.sql -O archive/911_last.sql
```

### 2. Проверьте, что миграции применены

```bash
cd ~/back911
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate
```

---

## 🚀 Запуск импорта данных

### Способ 1: Полный автоматический импорт (рекомендуется)

```bash
cd ~/back911

# Запустить скрипт импорта внутри контейнера
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web bash scripts/import_all_data.sh
```

**Что делает скрипт:**
1. ✅ Импортирует 82 города из SQL дампа
2. ✅ Импортирует 4 услуги
3. ✅ Импортирует 8 категорий техники
4. ✅ Импортирует 60+ опций услуг
5. ✅ Импортирует тысячи цен для всех комбинаций
6. ✅ Загружает статические данные (преимущества, метрики, контакты, ссылки на приложения)
7. ✅ Генерирует HTML контент для всех страниц
8. ✅ Генерирует SEO метаданные для ~400+ страниц

**Время выполнения:** 5-15 минут (зависит от размера дампа)

### Способ 2: Поэтапный импорт (если нужно контролировать процесс)

```bash
cd ~/back911

# 1. Импорт базовых данных
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_cities
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_services
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_technic_categories
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_options
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_prices

# 2. Загрузка статических данных
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py loaddata \
    website_api/fixtures/initial_advantages.json \
    website_api/fixtures/initial_metrics.json \
    website_api/fixtures/initial_contacts.json \
    website_api/fixtures/initial_app_links.json

# 3. Генерация контента
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content

# 4. Генерация SEO
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo
```

---

## 🔧 Дополнительные опции

### Указать путь к дампу

Если дамп находится в другом месте:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_cities --dump-path=/app/archive/911_last.sql
```

### Регенерировать существующий контент

Если нужно обновить контент или SEO:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content --regenerate
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_seo --regenerate
```

### Изменить размер батча для импорта цен

Если импорт цен занимает слишком много времени:

```bash
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_prices --batch-size=500
```

---

## ✅ Проверка результата

После импорта проверьте статистику:

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
- Cities: ~82
- Services: 4
- Options: ~60+
- Prices: тысячи (зависит от дампа)
- Service Content: сотни
- SEO Metadata: ~400+

---

## 🐛 Решение проблем

### Проблема 1: Файл дампа не найден

**Ошибка:**
```
Dump file not found: archive/911_last.sql
```

**Решение:**
1. Убедитесь, что файл существует в контейнере:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web ls -la archive/
   ```

2. Если файла нет, скопируйте его в контейнер:
   ```bash
   # Сначала скопируйте на сервер
   scp /path/to/911_last.sql root@45.144.221.92:~/back911/archive/
   
   # Затем скопируйте в контейнер (если нужно)
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml cp archive/911_last.sql back911-web-1:/app/archive/
   ```

### Проблема 2: Ошибки базы данных

**Ошибка:**
```
django.db.utils.OperationalError: ...
```

**Решение:**
1. Проверьте подключение к базе:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py dbshell
   ```

2. Убедитесь, что миграции применены:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate
   ```

### Проблема 3: Долгий импорт цен

Если импорт цен занимает очень много времени:

1. Уменьшите размер батча:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_prices --batch-size=100
   ```

2. Или запустите импорт в фоне:
   ```bash
   nohup docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py import_prices > import_prices.log 2>&1 &
   ```

### Проблема 4: Ошибки при генерации контента/SEO

Если генерация контента или SEO падает с ошибками:

1. Проверьте логи:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs web | tail -50
   ```

2. Попробуйте регенерировать с флагом `--regenerate`:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py generate_content --regenerate
   ```

---

## 📝 Пример полного процесса

```bash
# 1. Подключиться к серверу
ssh root@45.144.221.92

# 2. Перейти в директорию проекта
cd ~/back911

# 3. Убедиться, что контейнеры запущены
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml ps

# 4. Применить миграции (если еще не применены)
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 5. Запустить импорт
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web bash scripts/import_all_data.sh

# 6. Проверить результат
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "
from website_api.models import City, Service, Option, OptionPrice
print('Cities:', City.objects.count())
print('Services:', Service.objects.count())
print('Options:', Option.objects.count())
print('Prices:', OptionPrice.objects.count())
"
```

---

## ⚠️ Важные замечания

1. **Резервная копия:** Перед импортом рекомендуется сделать резервную копию базы данных:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec db pg_dump -U postgres website_911_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Время выполнения:** Полный импорт может занять 5-15 минут. Не прерывайте процесс!

3. **Повторный импорт:** Если запустить импорт повторно, данные могут дублироваться. Используйте `--regenerate` для обновления контента.

4. **Мониторинг:** Следите за логами во время импорта:
   ```bash
   docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs -f web
   ```

---

**Готово!** После успешного импорта ваш сайт будет полностью заполнен данными.

