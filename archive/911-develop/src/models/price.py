from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class OptionPrice(models.Model):

    class Meta:
        db_table = "option_price_db"
        verbose_name = "Цена опции"
        verbose_name_plural = "Цена опции"
        constraints = [
            models.UniqueConstraint(
                fields=["option", "city", "technic_category"],
                name="unique option price",
                violation_error_message="Цена для данной опции в этом городе и категории техники уже существует",
            )
        ]

    option = models.ForeignKey(
        "Option",
        related_name="prices",
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Опция",
    )
    city = models.ForeignKey(
        "City",
        related_name="prices",
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Город",
    )
    technic_category = models.ForeignKey(
        "TechnicCategory",
        related_name="prices",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Категория техники",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена",
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
