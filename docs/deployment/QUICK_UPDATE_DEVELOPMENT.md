# ⚡ Быстрое обновление с development ветки

## 📋 Команды для копирования на сервер

### Шаг 1: Подключение и переход в проект
```bash
ssh root@45.144.221.92
cd /opt/back911
```

### Шаг 2: Исправление ветки (использовать remotes/origin/development)
```bash
# Обновить информацию о удаленных ветках
git fetch origin

# Проверить, что remotes/origin/development существует
git branch -a | grep development

# Переключиться на development или создать из remotes/origin/development
git checkout development || git checkout -b development origin/development

# ВАЖНО: Проверить, что локальная ветка отслеживает remotes/origin/development
git branch -vv
# Должно показать: * development [origin/development] ...
```

### Шаг 3: Обновление кода из remotes/origin/development
```bash
# Обновить из удаленной ветки
git pull origin development

# Проверить последние коммиты
git log --oneline -3

# Проверить синхронизацию
git status
# Должно показать: "Your branch is up to date with 'origin/development'"
```

### Шаг 4: Остановка и пересборка
```bash
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod down
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod build --no-cache
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d
sleep 15
```

### Шаг 5: Миграции и статика
```bash
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --no-input
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --no-input
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod restart web
```

### Шаг 6: Проверка
```bash
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod ps
curl http://45.144.221.92/api/website/metrics/
```

---

## 🚀 Все команды одной строкой (для копирования)

```bash
cd /opt/back911 && git fetch origin && git checkout development || git checkout -b development origin/development && git branch -vv && git pull origin development && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod down && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod build --no-cache && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d && sleep 15 && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --no-input && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --no-input && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod restart web && docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod ps
```

**Примечание:** Команда `git branch -vv` покажет, отслеживает ли локальная ветка `remotes/origin/development`.

---

## 🔍 Проверка перед обновлением

```bash
# Проверить текущую ветку
git branch

# Проверить все ветки (включая remotes/origin/*)
git branch -a

# ВАЖНО: Проверить, что локальная ветка отслеживает remotes/origin/development
git branch -vv
# Должно показать: * development [origin/development] ...

# Проверить статус
git status

# Посмотреть последние коммиты в remotes/origin/development
git log --oneline origin/development -5

# Посмотреть последние коммиты в локальной ветке
git log --oneline -5
```

---

## ⚠️ Если на сервере неправильная ветка

```bash
# Удалить неправильную ветку (например, dev)
git branch -D dev

# Обновить информацию о удаленных ветках
git fetch origin

# Проверить, что remotes/origin/development существует
git branch -a | grep development

# Создать правильную ветку development из remotes/origin/development
git checkout -b development origin/development

# Проверить, что ветка правильно отслеживает remotes/origin/development
git branch -vv
# Должно показать: * development [origin/development] ...
```

