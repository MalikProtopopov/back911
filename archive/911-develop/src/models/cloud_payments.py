from django.db import models

from general_layout.models.abs_transaction import TransactionAbs
from src.models import Partner


class CloudPaymentsTransaction(TransactionAbs):

    class Meta:
        db_table = "cloud_payments_transaction_db"
        verbose_name = "Транзакция CloudPayments"
        verbose_name_plural = "Транзакции CloudPayments"
        ordering = ["-pk"]

    class TransactionStatuses(models.TextChoices):
        """Статусы транзакции"""

        created = "Created", "Создан"
        cancelled = "Cancelled", "Отменен"
        confirmed = "Completed", "Успешный одностадийный платеж"
        authorized = "Authorized", "Успешный двухстадийный платеж"

    status = models.CharField(
        max_length=100,
        choices=TransactionStatuses.choices,
        default=TransactionStatuses.created,
        verbose_name="Статус",
    )
    partner = models.ForeignKey(
        Partner,
        related_name="cloud_payments_transactions",
        verbose_name="Партнер",
        on_delete=models.PROTECT,
    )
