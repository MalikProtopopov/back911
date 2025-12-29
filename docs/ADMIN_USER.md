# Управление суперпользователем Django Admin

## Проверка наличия суперпользователя

### Способ 1: Через Django shell (рекомендуется)

```bash
# В Docker
docker compose exec web python manage.py shell

# В shell выполните:
from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
print(f"Найдено суперпользователей: {superusers.count()}")
for user in superusers:
    print(f"  - {user.username} ({user.email})")
```

### Способ 2: Через SQL запрос

```bash
# В Docker
docker compose exec db psql -U postgres -d website_911_db -c "SELECT username, email, is_superuser, is_staff FROM auth_user WHERE is_superuser = true;"
```

### Способ 3: Через кастомную команду

```bash
# Проверка через кастомную команду (покажет, существует ли пользователь)
docker compose exec web python manage.py create_admin --username admin --noinput
```

## Создание суперпользователя

### Способ 1: Стандартная команда Django (интерактивно)

```bash
# В Docker
docker compose exec web python manage.py createsuperuser

# Будет запрошено:
# Username: admin
# Email address: admin@911.ru
# Password: (введите пароль)
# Password (again): (повторите пароль)
```

### Способ 2: Кастомная команда (неинтерактивно)

```bash
# Создать с параметрами по умолчанию (admin/admin123)
docker compose exec web python manage.py create_admin --noinput

# Создать с кастомными параметрами
docker compose exec web python manage.py create_admin \
    --username admin \
    --email admin@911.ru \
    --password ваш_пароль \
    --noinput
```

### Способ 3: Через Django shell

```bash
docker compose exec web python manage.py shell
```

В shell выполните:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Проверка существования
if User.objects.filter(username='admin').exists():
    print("Пользователь уже существует!")
else:
    # Создание суперпользователя
    User.objects.create_superuser(
        username='admin',
        email='admin@911.ru',
        password='ваш_пароль'
    )
    print("Суперпользователь создан!")
```

## Обновление пароля суперпользователя

### Способ 1: Через Django shell

```bash
docker compose exec web python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='admin')
user.set_password('новый_пароль')
user.save()
print("Пароль обновлен!")
```

### Способ 2: Через кастомную команду

```bash
# Обновить пароль существующего пользователя
docker compose exec web python manage.py create_admin \
    --username admin \
    --password новый_пароль \
    --noinput
```

## Для Production окружения

Если используете переменную `COMPOSE_FILE`:

```bash
# Проверка
docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Суперпользователей: {User.objects.filter(is_superuser=True).count()}')"

# Создание
docker compose exec web python manage.py create_admin --noinput

# Или стандартная команда
docker compose exec web python manage.py createsuperuser
```

## Быстрая проверка одной командой

```bash
# Проверить количество суперпользователей
docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).count())"
```

Если результат `0` - суперпользователей нет, нужно создать.

## Проверка прав и доступов администратора

### Полная информация о суперпользователе

```bash
# На production сервере
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell
```

В shell выполните:
```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
User = get_user_model()

# Найти всех суперпользователей
superusers = User.objects.filter(is_superuser=True)

for user in superusers:
    print(f"\n{'='*60}")
    print(f"Пользователь: {user.username}")
    print(f"Email: {user.email}")
    print(f"Активен: {user.is_active}")
    print(f"Суперпользователь: {user.is_superuser}")
    print(f"Персонал (доступ к админке): {user.is_staff}")
    print(f"Дата регистрации: {user.date_joined}")
    print(f"Последний вход: {user.last_login}")
    
    # Группы пользователя
    groups = user.groups.all()
    if groups:
        print(f"Группы: {', '.join([g.name for g in groups])}")
    else:
        print("Группы: нет")
    
    # Разрешения (если не суперпользователь, будут показаны явные разрешения)
    if user.is_superuser:
        print("Разрешения: ВСЕ (суперпользователь имеет все права)")
    else:
        permissions = user.user_permissions.all()
        if permissions:
            print(f"Разрешения: {permissions.count()} явных разрешений")
        else:
            print("Разрешения: только через группы")
    
    # Проверка доступа к админ-панели
    can_access_admin = user.is_active and user.is_staff
    print(f"Доступ к админ-панели: {'✅ ДА' if can_access_admin else '❌ НЕТ'}")
```

### Быстрая проверка одной командой

```bash
# Проверить всех суперпользователей с их правами
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.filter(is_superuser=True):
    print(f'{user.username}: superuser={user.is_superuser}, staff={user.is_staff}, active={user.is_active}')
"
```

### Проверка через SQL (если нужен быстрый доступ)

```bash
# Все суперпользователи с их правами
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml exec db psql -U postgres -d website_911_db -c "
SELECT 
    username, 
    email, 
    is_superuser, 
    is_staff, 
    is_active,
    date_joined,
    last_login
FROM auth_user 
WHERE is_superuser = true OR is_staff = true
ORDER BY is_superuser DESC, username;
"
```

### Что означают флаги:

- **`is_superuser`** = `true`:
  - ✅ Полный доступ ко всем моделям в админ-панели
  - ✅ Может создавать/редактировать/удалять любые объекты
  - ✅ Может управлять пользователями и их правами
  - ✅ Обходит все проверки разрешений

- **`is_staff`** = `true`:
  - ✅ Доступ к админ-панели Django (`/admin/`)
  - ⚠️ Но права на редактирование зависят от `is_superuser` или явных разрешений

- **`is_active`** = `true`:
  - ✅ Пользователь может войти в систему
  - ❌ Если `false` - вход заблокирован

### Проверка доступа к конкретной модели

```python
from django.contrib.auth import get_user_model
from django.contrib import admin
from website_api.models import City, Service, Lead

User = get_user_model()
user = User.objects.get(username='admin')

# Проверить, может ли пользователь изменять модель
print(f"Может изменять City: {user.has_perm('website_api.change_city')}")
print(f"Может удалять Service: {user.has_perm('website_api.delete_service')}")
print(f"Может просматривать Lead: {user.has_perm('website_api.view_lead')}")

# Для суперпользователя все будет True
```

### Список всех доступных разрешений

```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Все разрешения для моделей website_api
permissions = Permission.objects.filter(
    content_type__app_label='website_api'
).order_by('content_type__model', 'codename')

for perm in permissions:
    print(f"{perm.content_type.app_label}.{perm.content_type.model}: {perm.codename}")
```

