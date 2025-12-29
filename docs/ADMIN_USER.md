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

