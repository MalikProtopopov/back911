# 🔄 Обновление сервера с ветки development

## ⚠️ Важно: Исправление проблемы с ветками

Если на сервере создалась новая dev ветка вместо использования существующей `development` из удаленного репозитория, выполните следующие команды:

## 📋 Команды для выполнения на сервере

### 1. Подключение к серверу

```bash
ssh root@45.144.221.92
# или
ssh your-user@45.144.221.92
```

### 2. Переход в директорию проекта

```bash
cd /opt/back911
# или туда, где у вас находится проект
```

### 3. Проверка текущего состояния

```bash
# Проверить текущую ветку
git branch

# Проверить все ветки (локальные и удаленные)
git branch -a

# Проверить, какие ветки отслеживают удаленные (ВАЖНО!)
git branch -vv

# Проверить статус
git status

# Проверить удаленные ветки
git remote show origin
```

### 4. Исправление проблемы с ветками (если нужно)

**⚠️ ВАЖНО:** Нужно использовать именно `remotes/origin/development`, а не создавать новую локальную ветку!

Если на сервере есть локальная ветка `dev` или другая неправильная ветка:

```bash
# Удалить неправильную локальную ветку (если она есть)
git branch -D dev

# Получить все удаленные ветки (обновить информацию о remotes/origin/*)
git fetch origin

# Проверить, что remotes/origin/development существует
git branch -a | grep development

# Переключиться на правильную ветку development из remotes/origin/development
git checkout development

# Если ветка development не существует локально, создать её из удаленной
# Это создаст локальную ветку, которая будет отслеживать remotes/origin/development
git checkout -b development origin/development

# Убедиться, что локальная ветка отслеживает remotes/origin/development
git branch -vv
# Должно показать: * development [origin/development] ...
```

**Проверка отслеживания:**
```bash
# Команда должна показать, что development отслеживает origin/development
git branch -vv
# Пример правильного вывода:
# * development ca8ca20 [origin/development] Add options API endpoint...
```

### 5. Обновление кода с ветки development (remotes/origin/development)

```bash
# Остановить контейнеры
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod down

# Получить последние изменения из удаленного репозитория
# Это обновит информацию о remotes/origin/development
git fetch origin

# Проверить, что remotes/origin/development обновлена
git log --oneline origin/development -3

# Переключиться на ветку development (если еще не на ней)
git checkout development

# Убедиться, что локальная ветка отслеживает remotes/origin/development
git branch -vv
# Должно показать: * development [origin/development] ...

# Обновить локальную ветку development из remotes/origin/development
git pull origin development
# Или просто: git pull (если ветка правильно отслеживает origin/development)

# Проверить, что обновление прошло успешно
git log --oneline -5

# Проверить, что локальная ветка синхронизирована с remotes/origin/development
git status
# Должно показать: "Your branch is up to date with 'origin/development'"
```

### 6. Пересборка и запуск

```bash
# Пересобрать образы
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod build --no-cache

# Запустить контейнеры
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d

# Подождать немного для запуска сервисов
sleep 15
```

### 7. Применение миграций и сбор статики

```bash
# Применить миграции (если AUTO_MIGRATE не включен)
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --no-input

# Собрать статику (если не собирается автоматически)
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --no-input
```

### 8. Перезапуск web сервиса

```bash
# Перезапустить web контейнер для применения изменений
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod restart web
```

### 9. Проверка статуса

```bash
# Проверить статус контейнеров
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod ps

# Проверить логи
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod logs -f web

# Проверить API
curl http://45.144.221.92/api/website/metrics/
```

## 🚀 Быстрая команда (все в одном)

Если вы уверены, что на сервере правильная ветка development, отслеживающая `remotes/origin/development`, можно выполнить все одной командой:

```bash
cd /opt/back911 && \
git fetch origin && \
git checkout development || git checkout -b development origin/development && \
git branch -vv && \
git pull origin development && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod down && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod build --no-cache && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d && \
sleep 15 && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --no-input && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --no-input && \
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod restart web
```

**Примечание:** Команда `git branch -vv` покажет, отслеживает ли локальная ветка `remotes/origin/development`.

## 🔧 Если используется скрипт update.sh

Если вы хотите использовать скрипт `update.sh`, но он тянет из `main`, временно измените его:

```bash
# Отредактировать скрипт
nano scripts/update.sh

# Найти строку:
# git pull origin main

# Заменить на:
# git pull origin development
```

Или создайте отдельный скрипт для development:

```bash
# Создать скрипт update-dev.sh
cat > scripts/update-dev.sh << 'EOF'
#!/bin/bash
set -e
cd /opt/back911
git fetch origin
git checkout development
git pull origin development
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod down
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod build
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d
sleep 15
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --no-input
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --no-input
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod restart web
EOF

chmod +x scripts/update-dev.sh
```

Затем используйте:
```bash
./scripts/update-dev.sh
```

## 📝 Проверка после обновления

```bash
# Проверить текущую ветку
git branch

# Проверить последний коммит
git log --oneline -1

# Проверить, что ветка синхронизирована с удаленной
git status

# Проверить работу API
curl http://45.144.221.92/api/website/metrics/
```

## ⚠️ Важные замечания

1. **Всегда проверяйте ветку перед обновлением**: `git branch`
2. **Убедитесь, что используете правильную удаленную ветку**: `git branch -a`
3. **Проверяйте логи после обновления**: `docker-compose logs -f web`
4. **Делайте бэкап базы данных перед миграциями** (если есть важные данные)

## 🆘 Решение проблем

### Проблема: "branch 'development' does not exist"

```bash
# Создать ветку из удаленной
git fetch origin
git checkout -b development origin/development
```

### Проблема: "Your branch and 'origin/development' have diverged"

```bash
# Сбросить локальную ветку на удаленную (ОСТОРОЖНО: потеряете локальные изменения!)
git fetch origin
git reset --hard origin/development
```

### Проблема: Конфликты при pull

```bash
# Сохранить текущие изменения
git stash

# Обновить из удаленной ветки
git pull origin development

# Применить сохраненные изменения (если нужно)
git stash pop
```

---

**Дата создания:** 2025-01-XX  
**Версия:** 1.0

