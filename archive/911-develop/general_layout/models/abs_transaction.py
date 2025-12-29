from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator


class TransactionAbs(models.Model):
    """Платежная транзакция"""

    class BalanceTypes(models.TextChoices):
        """Статусы транзакции"""

        deposit_balance = "deposit_balance", "Депозитный баланс"
        commission_balance = "commission_balance", "Комиссионный баланс"

    payment_id = models.CharField(
        max_length=100,
        verbose_name="ID платежа",
    )
    payment_url = models.CharField(
        max_length=255,
        verbose_name="Url платежа",
        null=True,
    )
    payment_token = models.CharField(
        max_length=255,
        verbose_name="Token платежа",
        null=True,
    )
    payment_data = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="Ответ платежной системы",
    )
    webhook_data = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="Ответ по web hook",
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    date_updated = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата обновления",
    )
    payment_artifact = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="url/token платежа",
    )
    order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Номер заказа транзакции",
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        verbose_name="Размер платежа",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    balance_type = models.CharField(
        max_length=100,
        choices=BalanceTypes.choices,
        verbose_name="Тип баланса",
    )

    class Meta:
        abstract = True
