# Руководство для бэкендера: Импорт данных из дампа приложения

## Обзор

Этот документ описывает процесс импорта данных из дампа мобильного приложения (`archive/911_last.sql`) в новую структуру БД сайта с динамическими параметрами.

---

## Структура дампа приложения

### Ключевые таблицы для импорта

| Таблица в дампе | Описание | Импортируется в |
|-----------------|----------|-----------------|
| `city_db` | Города | City (уже есть) |
| `service_db` | Услуги | Service (уже есть) |
| `option_db` | Опции услуг | Option (обновить has_parameters) |
| `option_price_db` | Цены опций | OptionPrice (уже есть) |
| `order_condition_db` | Модификаторы цен | ParameterType + ParameterValue + ParameterPrice |
| `working_zone_db` | Зоны доставки | DeliveryZone |
| `technic_category_db` | Категории техники | TechnicCategory (уже есть) |

---

## Шаг 1: Анализ данных в дампе

### 1.1 Извлечение городов

```sql
-- Из дампа 911_last.sql
SELECT id, title FROM city_db;
```

**Ожидаемый результат:**
```
1 | Махачкала
2 | Каспийск
3 | Дербент
...
```

### 1.2 Извлечение услуг

```sql
SELECT id, title FROM service_db;
```

**Ожидаемый результат:**
```
1 | Шиномонтаж
2 | Доставка топлива
3 | Эвакуатор
4 | Автовышка
```

### 1.3 Извлечение опций

```sql
SELECT id, title, service_id FROM option_db;
```

**Ожидаемый результат (примеры):**
```
1  | Устранение прокола (камерная) | 1
2  | Устранение прокола (бескамерная) | 1
3  | Снятие/Установка колеса | 1
10 | АИ-92 | 2
11 | АИ-95 | 2
20 | Эвакуация легкового автомобиля | 3
30 | Автовышка 10 метров | 4
31 | Автовышка 16 метров | 4
...
```

### 1.4 Извлечение condition_type (типы параметров)

```sql
SELECT DISTINCT condition_type FROM order_condition_db;
```

**Ожидаемый результат:**
```
radius
fuel_type
volume
hours
```

### 1.5 Извлечение условий (модификаторов)

```sql
SELECT 
    id, 
    title, 
    condition_type, 
    additional_price, 
    option_id 
FROM order_condition_db 
WHERE option_id IN (SELECT id FROM option_db WHERE service_id = 1)  -- Шиномонтаж
ORDER BY condition_type, title;
```

**Ожидаемый результат (радиусы для шиномонтажа):**
```
1  | R13 | radius | 0    | 1
2  | R14 | radius | 100  | 1
3  | R15 | radius | 200  | 1
4  | R16 | radius | 300  | 1
5  | R17 | radius | 400  | 1
6  | R18 | radius | 450  | 1
7  | R19 | radius | 500  | 1
8  | R20 | radius | 600  | 1
9  | R21 | radius | 700  | 1
10 | R22 | radius | 800  | 1
...
```

### 1.6 Извлечение зон доставки

```sql
SELECT 
    id, 
    title, 
    departure_price, 
    location_status, 
    city_id 
FROM working_zone_db 
WHERE city_id = 1;  -- Махачкала
```

**Ожидаемый результат:**
```
1 | В городе    | 0    | in_city  | 1
2 | За городом  | 1500 | out_city | 1
```

---

## Шаг 2: Создание management команд

### 2.1 Команда импорта типов параметров

```python
# website_api/management/commands/import_parameter_types.py

from django.core.management.base import BaseCommand
from website_api.models import ParameterType, ParameterValue


class Command(BaseCommand):
    help = 'Импорт типов параметров из дампа приложения'
    
    def handle(self, *args, **options):
        # Типы параметров из дампа
        parameter_types = [
            {
                'code': 'tire_radius',
                'title': 'Радиус шины',
                'description': 'Выберите радиус колеса',
                'values': [
                    ('R13', 'R13', 1),
                    ('R14', 'R14', 2),
                    ('R15', 'R15', 3),
                    ('R16', 'R16', 4),
                    ('R17', 'R17', 5),
                    ('R18', 'R18', 6),
                    ('R19', 'R19', 7),
                    ('R20', 'R20', 8),
                    ('R21', 'R21', 9),
                    ('R22', 'R22', 10),
                ]
            },
            {
                'code': 'fuel_type',
                'title': 'Тип топлива',
                'description': 'Выберите тип топлива',
                'values': [
                    ('ai92', 'АИ-92', 1),
                    ('ai95', 'АИ-95', 2),
                    ('ai98', 'АИ-98', 3),
                    ('diesel', 'ДТ', 4),
                ]
            },
            {
                'code': 'fuel_volume',
                'title': 'Объем топлива',
                'description': 'Выберите объем топлива',
                'values': [
                    ('10l', '10 литров', 1),
                    ('20l', '20 литров', 2),
                    ('30l', '30 литров', 3),
                    ('40l', '40 литров', 4),
                    ('50l', '50 литров', 5),
                ]
            },
            {
                'code': 'boom_height',
                'title': 'Высота автовышки',
                'description': 'Выберите высоту подъема',
                'values': [
                    ('10m', '10 метров', 1),
                    ('16m', '16 метров', 2),
                    ('22m', '22 метра', 3),
                ]
            },
        ]
        
        for pt_data in parameter_types:
            pt, created = ParameterType.objects.update_or_create(
                code=pt_data['code'],
                defaults={
                    'title': pt_data['title'],
                    'description': pt_data['description'],
                    'is_active': True,
                }
            )
            
            action = 'Создан' if created else 'Обновлен'
            self.stdout.write(f'{action} тип параметра: {pt.title}')
            
            # Создаем значения
            for value, display_name, sort_order in pt_data['values']:
                pv, created = ParameterValue.objects.update_or_create(
                    parameter_type=pt,
                    value=value,
                    defaults={
                        'display_name': display_name,
                        'sort_order': sort_order,
                        'is_active': True,
                    }
                )
                action = 'Создано' if created else 'Обновлено'
                self.stdout.write(f'  {action} значение: {pv.display_name}')
        
        self.stdout.write(self.style.SUCCESS('Импорт типов параметров завершен'))
```

### 2.2 Команда импорта зон доставки

```python
# website_api/management/commands/import_delivery_zones.py

from django.core.management.base import BaseCommand
from website_api.models import City, DeliveryZone


class Command(BaseCommand):
    help = 'Импорт зон доставки из дампа приложения'
    
    def handle(self, *args, **options):
        # Данные из дампа (working_zone_db)
        zones_data = [
            # (city_slug, zone_name, location_status, delivery_price)
            ('makhachkala', 'В городе', 'in_city', 0),
            ('makhachkala', 'За городом', 'out_city', 1500),
            ('kaspiysk', 'В городе', 'in_city', 0),
            ('kaspiysk', 'За городом', 'out_city', 1200),
            ('derbent', 'В городе', 'in_city', 0),
            ('derbent', 'За городом', 'out_city', 1800),
            # Добавьте остальные города из дампа
        ]
        
        for city_slug, zone_name, location_status, delivery_price in zones_data:
            try:
                city = City.objects.get(slug=city_slug)
            except City.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Город {city_slug} не найден, пропускаем')
                )
                continue
            
            zone, created = DeliveryZone.objects.update_or_create(
                city=city,
                location_status=location_status,
                defaults={
                    'zone_name': zone_name,
                    'delivery_price': delivery_price,
                    'is_active': True,
                }
            )
            
            action = 'Создана' if created else 'Обновлена'
            self.stdout.write(f'{action} зона: {city.title} - {zone_name}: {delivery_price} ₽')
        
        self.stdout.write(self.style.SUCCESS('Импорт зон доставки завершен'))
```

### 2.3 Команда связывания опций с параметрами

```python
# website_api/management/commands/link_options_to_parameters.py

from django.core.management.base import BaseCommand
from website_api.models import Option, ParameterType, OptionParameterType


class Command(BaseCommand):
    help = 'Связывание опций с типами параметров'
    
    def handle(self, *args, **options):
        # Маппинг: какие опции требуют какие параметры
        # Формат: (option_title_contains, parameter_type_code, is_required)
        option_parameter_links = [
            # Шиномонтаж - требует радиус шины
            ('Устранение прокола', 'tire_radius', True),
            ('Снятие/Установка колеса', 'tire_radius', True),
            ('Замена колеса', 'tire_radius', True),
            ('Балансировка', 'tire_radius', True),
            ('Накачка колеса', 'tire_radius', True),
            
            # Доставка топлива - требует тип и объем
            ('АИ-92', 'fuel_volume', True),
            ('АИ-95', 'fuel_volume', True),
            ('АИ-98', 'fuel_volume', True),
            ('ДТ', 'fuel_volume', True),
        ]
        
        for option_title_part, param_code, is_required in option_parameter_links:
            try:
                param_type = ParameterType.objects.get(code=param_code)
            except ParameterType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Тип параметра {param_code} не найден')
                )
                continue
            
            # Находим опции по части названия
            options = Option.objects.filter(title__icontains=option_title_part)
            
            for option in options:
                # Обновляем has_parameters
                option.has_parameters = True
                option.save()
                
                # Создаем связь
                link, created = OptionParameterType.objects.update_or_create(
                    option=option,
                    parameter_type=param_type,
                    defaults={'is_required': is_required}
                )
                
                action = 'Создана' if created else 'Обновлена'
                self.stdout.write(f'{action} связь: {option.title} → {param_type.title}')
        
        # Опции БЕЗ параметров (эвакуатор, автовышка)
        options_without_params = Option.objects.filter(
            has_parameters=False,
            service__slug__in=['evakuator', 'avtovyshka']
        )
        
        for option in options_without_params:
            self.stdout.write(f'Опция без параметров: {option.title}')
        
        self.stdout.write(self.style.SUCCESS('Связывание опций завершено'))
```

### 2.4 Команда импорта цен параметров

```python
# website_api/management/commands/import_parameter_prices.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from website_api.models import (
    Option, City, ParameterType, ParameterValue, 
    ParameterPrice, TechnicCategory
)


class Command(BaseCommand):
    help = 'Импорт цен параметров из дампа приложения'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            default='makhachkala',
            help='Slug города для импорта (по умолчанию: makhachkala)'
        )
    
    def handle(self, *args, **options):
        city_slug = options['city']
        
        try:
            city = City.objects.get(slug=city_slug)
        except City.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Город {city_slug} не найден'))
            return
        
        self.stdout.write(f'Импорт цен для города: {city.title}')
        
        # Данные из order_condition_db (примеры для Махачкалы)
        # Формат: (option_title, param_type_code, param_value, price_modifier, technic_category_title)
        price_data = [
            # Шиномонтаж - Устранение прокола (камерная)
            ('Устранение прокола (камерная)', 'tire_radius', 'R13', 0, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R14', 100, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R15', 200, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R16', 300, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R17', 400, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R18', 450, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R19', 500, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R20', 600, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R21', 700, None),
            ('Устранение прокола (камерная)', 'tire_radius', 'R22', 800, None),
            
            # Шиномонтаж - Снятие/Установка колеса
            ('Снятие/Установка колеса', 'tire_radius', 'R13', 0, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R14', 50, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R15', 100, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R16', 150, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R17', 200, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R18', 250, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R19', 300, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R20', 350, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R21', 400, None),
            ('Снятие/Установка колеса', 'tire_radius', 'R22', 450, None),
            
            # Добавьте остальные данные из дампа...
        ]
        
        for option_title, param_code, param_value, price_modifier, tc_title in price_data:
            try:
                option = Option.objects.get(title=option_title)
            except Option.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Опция "{option_title}" не найдена')
                )
                continue
            
            try:
                param_type = ParameterType.objects.get(code=param_code)
                param_value_obj = ParameterValue.objects.get(
                    parameter_type=param_type,
                    value=param_value
                )
            except (ParameterType.DoesNotExist, ParameterValue.DoesNotExist):
                self.stdout.write(
                    self.style.WARNING(f'Параметр {param_code}={param_value} не найден')
                )
                continue
            
            technic_category = None
            if tc_title:
                try:
                    technic_category = TechnicCategory.objects.get(title=tc_title)
                except TechnicCategory.DoesNotExist:
                    pass
            
            price, created = ParameterPrice.objects.update_or_create(
                option=option,
                parameter_value=param_value_obj,
                city=city,
                technic_category=technic_category,
                defaults={'price_modifier': Decimal(str(price_modifier))}
            )
            
            action = 'Создана' if created else 'Обновлена'
            self.stdout.write(
                f'{action}: {option.title} + {param_value_obj.display_name} = +{price_modifier} ₽'
            )
        
        self.stdout.write(self.style.SUCCESS(f'Импорт цен для {city.title} завершен'))
```

### 2.5 Главная команда импорта

```python
# website_api/management/commands/import_all_pricing_data.py

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Импорт всех данных ценообразования из дампа приложения'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-cities',
            action='store_true',
            help='Пропустить импорт городов (если уже есть)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('Начинаем импорт данных ценообразования'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        # 1. Импорт типов параметров и значений
        self.stdout.write('\n' + '=' * 40)
        self.stdout.write('Шаг 1: Импорт типов параметров')
        self.stdout.write('=' * 40)
        call_command('import_parameter_types')
        
        # 2. Импорт зон доставки
        self.stdout.write('\n' + '=' * 40)
        self.stdout.write('Шаг 2: Импорт зон доставки')
        self.stdout.write('=' * 40)
        call_command('import_delivery_zones')
        
        # 3. Связывание опций с параметрами
        self.stdout.write('\n' + '=' * 40)
        self.stdout.write('Шаг 3: Связывание опций с параметрами')
        self.stdout.write('=' * 40)
        call_command('link_options_to_parameters')
        
        # 4. Импорт цен параметров для каждого города
        self.stdout.write('\n' + '=' * 40)
        self.stdout.write('Шаг 4: Импорт цен параметров')
        self.stdout.write('=' * 40)
        
        cities = ['makhachkala', 'kaspiysk', 'derbent']
        for city_slug in cities:
            self.stdout.write(f'\nИмпорт цен для {city_slug}...')
            call_command('import_parameter_prices', city=city_slug)
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Импорт данных ценообразования завершен!'))
        self.stdout.write('=' * 60)
```

---

## Шаг 3: Запуск импорта

### 3.1 Применение миграций

```bash
# Создаем миграции для новых моделей
python manage.py makemigrations website_api

# Применяем миграции
python manage.py migrate
```

### 3.2 Запуск полного импорта

```bash
# Импорт всех данных
python manage.py import_all_pricing_data
```

### 3.3 Поэтапный импорт (для отладки)

```bash
# Шаг 1: Типы параметров
python manage.py import_parameter_types

# Шаг 2: Зоны доставки
python manage.py import_delivery_zones

# Шаг 3: Связи опций
python manage.py link_options_to_parameters

# Шаг 4: Цены параметров (по городам)
python manage.py import_parameter_prices --city=makhachkala
python manage.py import_parameter_prices --city=kaspiysk
python manage.py import_parameter_prices --city=derbent
```

---

## Шаг 4: Проверка импорта

### 4.1 Проверка в Django shell

```python
python manage.py shell

from website_api.models import *

# Проверяем типы параметров
print(f"Типов параметров: {ParameterType.objects.count()}")
for pt in ParameterType.objects.all():
    print(f"  {pt.code}: {pt.title} ({pt.values.count()} значений)")

# Проверяем зоны доставки
print(f"\nЗон доставки: {DeliveryZone.objects.count()}")
for zone in DeliveryZone.objects.select_related('city')[:10]:
    print(f"  {zone.city.title}: {zone.zone_name} = {zone.delivery_price} ₽")

# Проверяем опции с параметрами
print(f"\nОпций с параметрами: {Option.objects.filter(has_parameters=True).count()}")
print(f"Опций без параметров: {Option.objects.filter(has_parameters=False).count()}")

# Проверяем цены параметров
print(f"\nЦен параметров: {ParameterPrice.objects.count()}")
```

### 4.2 Тест API

```bash
# Проверяем новые endpoints
curl http://localhost:8000/api/pricing/parameter-types/

curl http://localhost:8000/api/pricing/parameter-types/tire_radius/values/

curl http://localhost:8000/api/pricing/cities/1/delivery-zones/

# Тест расчета цены
curl -X POST http://localhost:8000/api/pricing/calculate/ \
  -H "Content-Type: application/json" \
  -d '{
    "option_id": 1,
    "city_id": 1,
    "parameter_values": {"tire_radius": 7},
    "delivery_zone_id": 2
  }'
```

---

## Шаг 5: Создание fixtures

После успешного импорта можно создать fixtures для быстрого развертывания:

```bash
# Экспорт в fixtures
python manage.py dumpdata website_api.ParameterType \
  --indent=2 > website_api/fixtures/parameter_types.json

python manage.py dumpdata website_api.ParameterValue \
  --indent=2 > website_api/fixtures/parameter_values.json

python manage.py dumpdata website_api.DeliveryZone \
  --indent=2 > website_api/fixtures/delivery_zones.json

python manage.py dumpdata website_api.OptionParameterType \
  --indent=2 > website_api/fixtures/option_parameter_types.json

python manage.py dumpdata website_api.ParameterPrice \
  --indent=2 > website_api/fixtures/parameter_prices.json
```

### Загрузка fixtures

```bash
python manage.py loaddata parameter_types
python manage.py loaddata parameter_values
python manage.py loaddata delivery_zones
python manage.py loaddata option_parameter_types
python manage.py loaddata parameter_prices
```

---

## Маппинг таблиц: Дамп → Сайт

| Дамп (таблица) | Дамп (поле) | Сайт (модель) | Сайт (поле) |
|----------------|-------------|---------------|-------------|
| `city_db` | `id` | `City` | `id` |
| `city_db` | `title` | `City` | `title` |
| `service_db` | `id` | `Service` | `id` |
| `service_db` | `title` | `Service` | `title` |
| `option_db` | `id` | `Option` | `id` |
| `option_db` | `title` | `Option` | `title` |
| `option_db` | `service_id` | `Option` | `service_id` |
| `option_price_db` | `amount` | `OptionPrice` | `amount` |
| `option_price_db` | `city_id` | `OptionPrice` | `city_id` |
| `option_price_db` | `option_id` | `OptionPrice` | `option_id` |
| `order_condition_db` | `condition_type` | `ParameterType` | `code` |
| `order_condition_db` | `title` | `ParameterValue` | `display_name` |
| `order_condition_db` | `additional_price` | `ParameterPrice` | `price_modifier` |
| `working_zone_db` | `title` | `DeliveryZone` | `zone_name` |
| `working_zone_db` | `location_status` | `DeliveryZone` | `location_status` |
| `working_zone_db` | `departure_price` | `DeliveryZone` | `delivery_price` |

---

## Troubleshooting

### Проблема: Дубликаты при импорте

**Решение:** Используйте `update_or_create` вместо `create`:

```python
obj, created = Model.objects.update_or_create(
    unique_field=value,
    defaults={...}
)
```

### Проблема: Нет связи между городом в дампе и сайте

**Решение:** Создайте маппинг ID → slug:

```python
CITY_MAPPING = {
    1: 'makhachkala',
    2: 'kaspiysk',
    3: 'derbent',
    # ...
}
```

### Проблема: Разные названия опций

**Решение:** Используйте `icontains` или создайте маппинг:

```python
OPTION_MAPPING = {
    'Устранение прокола (камерная)': 'Устранение прокола камерная',
    # ...
}
```

---

## Контакты

Если есть вопросы по импорту — создайте issue или обратитесь к lead-разработчику.

