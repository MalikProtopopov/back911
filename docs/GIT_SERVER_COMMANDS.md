# Команды для работы с Git на удаленном сервере

## 🔄 Базовые команды для загрузки ветки

### 1. Подключение к серверу и переход в директорию проекта

```bash
# Подключиться к серверу (замените на ваш способ подключения)
ssh user@your-server.com

# Перейти в директорию проекта
cd /path/to/911_backend_website
```

### 2. Проверка текущего состояния

```bash
# Проверить текущую ветку
git branch

# Проверить статус изменений
git status

# Посмотреть последние коммиты
git log --oneline -5
```

### 3. Получить все обновления с удаленного репозитория

```bash
# Подтянуть все ветки и обновления
git fetch --all

# Или конкретную ветку
git fetch origin development
git fetch origin main
```

### 4. Переключиться на нужную ветку

```bash
# Переключиться на ветку development
git checkout development

# Или если ветки еще нет локально, создать и переключиться
git checkout -b development origin/development
```

### 5. Обновить текущую ветку

```bash
# Обновить ветку development
git pull origin development

# Или если уже на ветке development
git pull
```

## 📋 Полная последовательность для загрузки ветки development

```bash
# 1. Перейти в директорию проекта
cd /path/to/911_backend_website

# 2. Подтянуть все обновления
git fetch --all

# 3. Переключиться на ветку development
git checkout development

# 4. Обновить ветку до последней версии
git pull origin development

# 5. Проверить что все обновлено
git log --oneline -5
```

## 🔀 Переключение между ветками

```bash
# Сохранить текущие изменения (если есть)
git stash

# Переключиться на другую ветку
git checkout main
git checkout development

# Вернуть сохраненные изменения
git stash pop
```

## 🆕 Создание новой ветки на основе удаленной

```bash
# Создать локальную ветку на основе удаленной
git checkout -b development origin/development

# Или для main
git checkout -b main origin/main
```

## 🔍 Просмотр всех веток

```bash
# Локальные ветки
git branch

# Все ветки (локальные + удаленные)
git branch -a

# Только удаленные ветки
git branch -r
```

## ⚠️ Если есть локальные изменения

```bash
# Вариант 1: Сохранить изменения во временное хранилище
git stash
git pull origin development
git stash pop

# Вариант 2: Отменить все локальные изменения (ОСТОРОЖНО!)
git reset --hard origin/development

# Вариант 3: Закоммитить изменения перед обновлением
git add .
git commit -m "Local changes"
git pull origin development
```

## 🐳 После обновления кода (для Docker)

```bash
# Пересобрать и перезапустить контейнеры
cd /path/to/911_backend_website/docker
docker-compose -f docker-compose.prod.yml build web
docker-compose -f docker-compose.prod.yml up -d

# Или если используете dev окружение
docker-compose -f docker-compose.dev.yml build web
docker-compose -f docker-compose.dev.yml up -d
```

## 📝 Пример для production сервера

```bash
# 1. Подключиться к серверу
ssh user@production-server.com

# 2. Перейти в директорию проекта
cd /var/www/911_backend_website

# 3. Подтянуть обновления
git fetch --all

# 4. Переключиться на нужную ветку (например, main для production)
git checkout main
git pull origin main

# 5. Пересобрать Docker контейнеры
cd docker
docker-compose -f docker-compose.prod.yml build web
docker-compose -f docker-compose.prod.yml up -d

# 6. Применить миграции (если нужно)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 7. Собрать статические файлы (если нужно)
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

## 🔐 Если требуется аутентификация

```bash
# Если используете SSH ключи (рекомендуется)
# Убедитесь что SSH ключ добавлен в ssh-agent
ssh-add ~/.ssh/id_rsa

# Если используете HTTPS с токеном
git config --global credential.helper store
# При первом запросе введите токен вместо пароля
```

## ✅ Проверка что все работает

```bash
# Проверить текущую ветку и последний коммит
git branch
git log -1

# Проверить что нет несохраненных изменений
git status

# Проверить что ветка синхронизирована с удаленной
git status -sb
```

