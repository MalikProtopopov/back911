from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class DepositMinimum(models.Model):
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Минимальный депозит",
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super(DepositMinimum, self).save(*args, **kwargs)
