from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from general_layout.models.abs_service_and_option import OptionAbs
from src.models.price import OptionPrice


class Option(OptionAbs):

    class Meta:
        db_table = "option_db"
        verbose_name = "Опция"
        verbose_name_plural = "Опции"

    cities = models.ManyToManyField(
        "City", related_name="options", through=OptionPrice, verbose_name="Город"
    )
    service = models.ForeignKey(
        "Service",
        related_name="options",
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Услуга",
    )

    def __str__(self):
        return self.title


class PartnerServiceOption(models.Model):

    class Meta:
        db_table = "partner_service_option_db"
        verbose_name = "Опция c услугой партнера"
        verbose_name_plural = "Опции с услугами партнера"
        constraints = [
            models.UniqueConstraint(
                fields=["option", "partner_service"],
                name="unique option of partner service",
                violation_error_message="Такая опция уже есть",
            )
        ]

    option = models.ForeignKey(
        Option,
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Опция",
    )
    partner_service = models.ForeignKey(
        "PartnerService",
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Услуга партнера с верификацией",
    )


class OrderOption(models.Model):

    class Meta:
        db_table = "order_option_db"
        verbose_name = "Заказ с опцией"
        verbose_name_plural = "Заказы с опциями"
        constraints = [
            models.UniqueConstraint(
                fields=["option", "order"],
                name="unique option of order",
                violation_error_message="Такая опция уже есть",
            )
        ]

    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Опция",
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Заказ",
    )
    quantity = models.SmallIntegerField(
        default=1,
        verbose_name="Количество",
        validators=[
            MinValueValidator(1, message="Минимальное количество: 1"),
            MaxValueValidator(10, message="Максимальное количество: 10"),
        ],
    )
