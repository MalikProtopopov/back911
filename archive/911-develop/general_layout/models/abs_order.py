from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class OrderAbs(models.Model):
    """Заказ"""

    class OrderStatuses(models.TextChoices):
        new = "new", "Создан"
        on_the_way = "on_the_way", "В пути"
        in_progress = "in_progress", "В процессе выполнения"
        on_confirmation = "on_confirmation", "На подтверждении"
        done = "done", "Выполнен"
        cancelled = "cancelled", "Отменен"

    class Meta:
        abstract = True

    point_coordinates = models.JSONField(default=list)
    comment = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Комментарий к заказу"
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Итоговая цена",
    )
    options_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена опций",
    )
    delivery_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена опций",
    )
    status = models.CharField(
        max_length=50,
        choices=OrderStatuses.choices,
        default=OrderStatuses.new,
        db_index=True,
        verbose_name="Статус заказа",
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата, время создания заказа"
    )
    datetime_updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата, время обновления заказа"
    )
    address = models.CharField(max_length=255, verbose_name="Адрес")
    conditions = models.JSONField(
        default=list, null=True, blank=True, verbose_name="Условия заказа"
    )
    commission = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Комиссия, которую заплатит партнер",
    )
    technic_brand_model = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Техника клиента"
    )
    change_history = models.JSONField(
        default=dict, null=True, blank=True, verbose_name="История изменений опций"
    )
