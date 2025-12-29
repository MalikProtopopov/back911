# 📋 Команды для сервера 45.144.221.92

## 🚀 Первоначальная настройка (выполнить один раз)

### 1. Подключение и установка Docker

```bash
ssh root@45.144.221.92

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install docker-compose-plugin -y

# Установка Git
apt-get install git -y
```

### 2. Клонирование проекта

```bash
cd /opt
git clone https://github.com/MalikProtopopov/back911.git
cd back911
```

### 3. Создание .env.prod

```bash
nano .env.prod
```

**Скопируйте содержимое из файла `env.prod.template` и замените:**
- `SECRET_KEY` - сгенерируйте командой ниже
- `DB_PASSWORD` - придумайте сильный пароль
- Остальные значения при необходимости

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Первый запуск

```bash
chmod +x deploy.sh update.sh
./deploy.sh
```

Или вручную:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 🔄 Обновление проекта (после каждого изменения кода)

```bash
cd /opt/back911
./update.sh
```

Или вручную:
```bash
cd /opt/back911
docker-compose -f docker-compose.prod.yml down
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker-compose -f docker-compose.prod.yml restart web
```

## 📊 Полезные команды

### Проверка статуса
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Просмотр логов
```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Только web
docker-compose -f docker-compose.prod.yml logs -f web
```

### Перезапуск
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Остановка
```bash
docker-compose -f docker-compose.prod.yml down
```

### Проверка API
```bash
curl http://45.144.221.92/api/website/metrics/
```

---

**IP сервера:** 45.144.221.92

