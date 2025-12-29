# Анализ реализации опций и цен: Мобильное приложение vs Корпоративный сайт

## 📊 Текущая реализация в мобильном приложении (archive/911-develop)

### Архитектура данных

```
Option (Опция)
  ├── service (услуга)
  └── cities (города) - через OptionPrice (many-to-many)

OptionPrice (Цена опции)
  ├── option (опция)
  ├── city (город) ⭐ ОБЯЗАТЕЛЬНО
  ├── technic_category (категория техники) - опционально
  ├── amount (цена)
  └── order_conditions (условия заказа) - дополнительные наценки
```

### Ключевые особенности:

#### 1. **Цены привязаны к городу** ✅
```python
# archive/911-develop/src/models/price.py
class OptionPrice(models.Model):
    option = models.ForeignKey("Option", ...)
    city = models.ForeignKey("City", ...)  # ⭐ ГОРОД ОБЯЗАТЕЛЕН
    technic_category = models.ForeignKey("TechnicCategory", null=True, ...)
    amount = models.DecimalField(...)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["option", "city", "technic_category"],
                name="unique option price"
            )
        ]
```

**Вывод:** В мобильном приложении **НЕТ глобальных цен**. Каждая опция имеет индивидуальную цену для каждого города.

#### 2. **Категории техники** (дифференциация цен)

Цены могут различаться в зависимости от категории техники:
- Легковой автомобиль
- Кроссовер
- Внедорожник
- Легкий коммерческий транспорт
- Мотоцикл

**Пример:** Шиномонтаж R15 в Москве:
- Легковой: 300₽
- Кроссовер: 400₽
- Внедорожник: 500₽

#### 3. **OrderConditions** (дополнительные условия)

Система позволяет добавлять дополнительные наценки к базовой цене:

```python
class OrderConditions(models.Model):
    class ConditionTypes(models.TextChoices):
        radius = "radius", "Радиус колеса"
        fuel_type = "fuel_type", "Тип топлива"
    
    title = models.CharField(...)  # Например: "R13", "R14", "Дизель"
    condition_type = models.CharField(...)
    option = models.ForeignKey("OptionPrice", ...)  # ⭐ Привязано к OptionPrice
    additional_price = models.DecimalField(...)  # Дополнительная наценка
```

**Пример использования:**
```
Базовая опция: "Балансировка колеса" в Москве = 200₽

OrderConditions:
- R13: +0₽ (200₽ итого)
- R14: +50₽ (250₽ итого)
- R15: +100₽ (300₽ итого)
- R16: +150₽ (350₽ итого)
```

#### 4. **Расчет итоговой цены**

```python
# archive/911-develop/src/serializers/order_serializer.py
def _calculate_options_price(self, options_with_quantity, technic_category_id, city_id, conditions):
    # 1. Получаем базовую цену из OptionPrice
    if technic_category_id:
        options_price_qs = OptionPrice.objects.filter(
            option_id__in=option_ids,
            technic_category_id=technic_category_id,
            city_id=city_id,  # ⭐ Город обязателен
        )
    else:
        options_price_qs = OptionPrice.objects.filter(
            option_id__in=option_ids,
            technic_category_id__isnull=True,
            city_id=city_id,  # ⭐ Город обязателен
        )
    
    # 2. Добавляем дополнительные условия
    additional_price = self._calculate_additional_price(conditions, options_price_qs)
    
    # 3. Умножаем на количество
    for option_id, quantity in options_with_quantity:
        option_price = option_prices_dict.get(option_id)
        options_price_sum += option_price * quantity
    
    return options_price_sum + additional_price
```

---

## 📊 Текущая реализация на корпоративном сайте

### Архитектура данных

```
Option (Опция)
  ├── service (услуга)
  └── is_active (активность)

OptionPrice (Цена опции)
  ├── option (опция)
  ├── city (город) ⭐ ЕСТЬ
  ├── technic_category (категория техники) - опционально
  └── amount (цена)
```

### Ключевые особенности:

✅ **Архитектура ИДЕНТИЧНА мобильному приложению**
- Цены привязаны к городам
- Поддержка категорий техники
- Уникальность: (option, city, technic_category)

❌ **Чего НЕТ на сайте:**
- OrderConditions (дополнительные условия/наценки)
- Связь many-to-many между Option и City через OptionPrice

---

## 🎯 Рекомендации для корпоративного сайта

### ✅ Что делать ПРАВИЛЬНО:

#### 1. **Использовать индивидуальные цены по городам** (как в приложении)

**Причины:**
- ✅ Гибкость ценообразования (Москва дороже, регионы дешевле)
- ✅ Учет региональной экономики
- ✅ Конкурентоспособность в разных регионах
- ✅ Единая база данных с мобильным приложением
- ✅ Простая синхронизация цен

**Реализация уже есть:**
```python
# website_api/models/option_price.py
class OptionPrice(models.Model):
    option = models.ForeignKey('Option', ...)
    city = models.ForeignKey('City', ...)  # ⭐ УЖЕ ЕСТЬ
    technic_category = models.ForeignKey('TechnicCategory', null=True, ...)
    amount = models.DecimalField(...)
    
    class Meta:
        unique_together = ['option', 'city', 'technic_category']
```

#### 2. **Добавить OrderConditions для гибкого ценообразования**

Это позволит:
- Не создавать отдельные опции для каждого радиуса колеса
- Динамически добавлять наценки
- Упростить управление ценами

**Пример:** Вместо создания 10 опций:
```
❌ Плохо:
- "Балансировка R13" - 200₽
- "Балансировка R14" - 250₽
- "Балансировка R15" - 300₽
...
```

Создаем 1 опцию + условия:
```
✅ Хорошо:
Опция: "Балансировка колеса" (базовая цена 200₽)

Условия (OrderConditions):
- R13: +0₽
- R14: +50₽
- R15: +100₽
...
```

#### 3. **Модель для добавления на сайт**

```python
# website_api/models/option_condition.py
from django.db import models
from decimal import Decimal

class OptionCondition(models.Model):
    """Дополнительные условия/наценки к опции"""
    
    class ConditionTypes(models.TextChoices):
        RADIUS = "radius", "Радиус колеса"
        FUEL_TYPE = "fuel_type", "Тип топлива"
        VOLUME = "volume", "Объем"
        HOURS = "hours", "Часы"
    
    option_price = models.ForeignKey(
        'OptionPrice',
        on_delete=models.CASCADE,
        related_name='conditions',
        verbose_name="Цена опции"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название условия",
        help_text="Например: R13, R14, Дизель, 5 литров"
    )
    condition_type = models.CharField(
        max_length=100,
        choices=ConditionTypes.choices,
        verbose_name="Тип условия"
    )
    additional_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Дополнительная цена",
        help_text="Наценка к базовой цене опции"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )
    
    class Meta:
        db_table = "option_condition"
        verbose_name = "Условие опции"
        verbose_name_plural = "Условия опций"
        unique_together = ['option_price', 'title', 'condition_type']
        indexes = [
            models.Index(fields=['option_price', 'condition_type']),
        ]
    
    def __str__(self):
        return f"{self.option_price.option.title} - {self.title}: +{self.additional_price}₽"
```

---

## 📋 Сценарии использования

### Сценарий 1: Шиномонтаж с радиусами колес

```
Опция: "Перекидка комплекта"
Города: Москва, Санкт-Петербург

OptionPrice (Москва, Легковой):
├── Базовая цена: 1000₽
└── Условия:
    ├── R13: +0₽ → 1000₽
    ├── R14: +200₽ → 1200₽
    ├── R15: +400₽ → 1400₽
    ├── R16: +600₽ → 1600₽
    └── R17+: +1000₽ → 2000₽

OptionPrice (Санкт-Петербург, Легковой):
├── Базовая цена: 900₽  ← Дешевле в регионе
└── Условия:
    ├── R13: +0₽ → 900₽
    ├── R14: +150₽ → 1050₽
    └── ...
```

### Сценарий 2: Доставка топлива

```
Опция: "Доставка топлива"
Города: Москва

OptionPrice (Москва):
├── Базовая цена: 500₽ (включает до 5л)
└── Условия:
    ├── 5 литров: +0₽ → 500₽
    ├── 10 литров: +200₽ → 700₽
    ├── 20 литров: +500₽ → 1000₽
    ├── Дизель: +100₽ (дополнительная наценка)
    └── АИ-98: +150₽
```

### Сценарий 3: Эвакуатор с категориями техники

```
Опция: "Эвакуация до 10 км"
Город: Москва

OptionPrice (Москва, Легковой):
└── Цена: 2000₽

OptionPrice (Москва, Кроссовер):
└── Цена: 2500₽

OptionPrice (Москва, Внедорожник):
└── Цена: 3000₽
```

---

## 🚀 План миграции на сайте

### Этап 1: Текущее состояние (уже реализовано) ✅

```
Option → OptionPrice (city, technic_category, amount)
```

**Что работает:**
- Цены по городам ✅
- Категории техники ✅
- API эндпоинты ✅

### Этап 2: Добавить OptionCondition (рекомендуется)

**Новые возможности:**
- Гибкое ценообразование
- Меньше дублирования опций
- Проще управлять ценами
- Совместимость с мобильным приложением

**Файлы для создания:**
1. `website_api/models/option_condition.py` - модель
2. Миграция Django
3. `website_api/serializers/option.py` - добавить serializer
4. `website_api/admin.py` - админка для управления
5. API эндпоинт для получения условий (опционально)

### Этап 3: Синхронизация с мобильным приложением

Если планируется единая база данных:
- Переименовать таблицы: `option` → `option_db`, `option_price` → `option_price_db`
- Убедиться в совместимости моделей
- Настроить роутинг БД (если разные БД)

---

## ⚖️ Сравнение: Глобальные vs Индивидуальные цены

### ❌ Глобальные цены (одна цена для всех городов)

**Минусы:**
- Нет гибкости по регионам
- Москва и маленький город имеют одну цену
- Сложно конкурировать в регионах
- Несовместимость с мобильным приложением

**Плюсы:**
- Проще администрировать (меньше записей)

### ✅ Индивидуальные цены по городам (как в приложении)

**Плюсы:**
- ✅ Гибкость ценообразования
- ✅ Учет региональной экономики
- ✅ Конкурентоспособность
- ✅ Совместимость с мобильным приложением
- ✅ Возможность акций по городам

**Минусы:**
- Больше записей в БД (не критично)
- Нужно настраивать цены для каждого города

---

## 💡 Рекомендации

### 1. **Для корпоративного сайта: используйте индивидуальные цены по городам** ✅

Текущая реализация уже правильная! У вас есть:
- `OptionPrice` с привязкой к городу
- Категории техники
- API эндпоинты

### 2. **Добавьте OptionCondition для гибкости** (опционально, но рекомендуется)

Это упростит управление и уменьшит количество опций.

### 3. **Примеры из базы данных**

Проверьте текущие данные:
```bash
# Сколько опций без цен?
curl http://localhost:8000/api/website/options/ | grep -c "id"

# Сколько городов?
curl http://localhost:8000/api/website/cities/ | grep -c "id"

# Пример опции с ценами
curl http://localhost:8000/api/website/options/1/
```

### 4. **Создание цен для всех городов**

Если нужно быстро заполнить цены:

```python
# management/commands/populate_option_prices.py
from django.core.management.base import BaseCommand
from website_api.models import Option, City, OptionPrice
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cities = City.objects.filter(is_active=True)
        options = Option.objects.filter(is_active=True)
        
        base_prices = {
            'Балансировка': 200,
            'Перекидка комплекта': 1000,
            'Доставка топлива': 500,
            # ...
        }
        
        for option in options:
            base_price = Decimal(base_prices.get(option.title, 100))
            
            for city in cities:
                # Регионы дешевле на 20%
                multiplier = Decimal("0.8") if city.id > 2 else Decimal("1.0")
                price = base_price * multiplier
                
                OptionPrice.objects.get_or_create(
                    option=option,
                    city=city,
                    technic_category=None,
                    defaults={'amount': price}
                )
```

---

## 📊 Итоговая таблица

| Параметр | Мобильное приложение | Корпоративный сайт | Рекомендация |
|----------|---------------------|-------------------|--------------|
| Цены по городам | ✅ Есть | ✅ Есть | ✅ Оставить |
| Категории техники | ✅ Есть | ✅ Есть | ✅ Оставить |
| OptionConditions | ✅ Есть | ❌ Нет | ⚠️ Добавить |
| Many-to-many Option↔City | ✅ Есть | ❌ Нет | ℹ️ Опционально |
| API эндпоинты | ✅ Есть | ✅ Есть | ✅ OK |

---

## 🎯 Вывод

**Ваша текущая реализация на сайте ПРАВИЛЬНАЯ!** ✅

Вы уже используете индивидуальные цены по городам, как в мобильном приложении. Это правильный подход.

**Дополнительно рекомендуется:**
1. Добавить модель `OptionCondition` для гибкого ценообразования
2. Это упростит управление и уменьшит дублирование опций
3. Будет полная совместимость с мобильным приложением

**НЕ делайте глобальные цены!** Это шаг назад.

