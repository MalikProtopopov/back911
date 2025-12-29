from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class WorkingZoneAbs(models.Model):
    """Рабочая зона"""

    class LocationStatuses(models.TextChoices):
        in_city = "in_city", "В пределах города"
        out_city = "out_city", "За пределами города"

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название зоны",
    )
    area_coordinates = models.JSONField(
        default=list,
        verbose_name="Координаты зоны",
    )
    departure_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена доставки",
    )
    fuel_delivery_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена доставки топлива",
    )
    location_status = models.CharField(
        choices=LocationStatuses.choices,
        null=True,
        blank=True,
        verbose_name="Статус зоны",
    )
