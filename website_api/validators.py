"""Price validators for the pricing system"""
from decimal import Decimal
from django.core.exceptions import ValidationError


MIN_PRICE = Decimal('0')
MAX_PRICE = Decimal('1000000')


def validate_price(value):
    """
    Валидация цены.
    
    - Цена не может быть отрицательной
    - Цена не может превышать 1 000 000
    """
    if value < MIN_PRICE:
        raise ValidationError('Цена не может быть отрицательной')
    if value > MAX_PRICE:
        raise ValidationError(f'Цена не может быть больше {MAX_PRICE}')
    return value


def validate_price_modifier(value):
    """
    Валидация модификатора цены.
    
    Модификатор может быть отрицательным (для скидок),
    но не может быть слишком большим по абсолютному значению.
    """
    if value < -MAX_PRICE:
        raise ValidationError(f'Модификатор не может быть меньше -{MAX_PRICE}')
    if value > MAX_PRICE:
        raise ValidationError(f'Модификатор не может быть больше {MAX_PRICE}')
    return value


def validate_positive_price(value):
    """
    Валидация строго положительной цены.
    
    Используется для цен, которые не могут быть нулевыми (например, цена услуги).
    """
    if value <= 0:
        raise ValidationError('Цена должна быть больше нуля')
    if value > MAX_PRICE:
        raise ValidationError(f'Цена не может быть больше {MAX_PRICE}')
    return value

