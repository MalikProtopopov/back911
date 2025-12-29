from django.db import models

from general_layout.models.abs_transaction import TransactionAbs
from src.models import Partner


class TinkoffTransaction(TransactionAbs):

    class Meta:
        db_table = "tinkoff_transaction_db"
        verbose_name = "Транзакция Tinkoff"
        verbose_name_plural = "Транзакции Tinkoff"
        ordering = ["-pk"]

    class TransactionStatuses(models.TextChoices):
        """Статусы транзакции"""

        in_progress = "IN_PROGRESS", "В процессе исполнения"
        rejected = "REJECTED", "Платеж отклонен"
        confirmed = "CONFIRMED", "Успешный одностадийный платеж"
        authorized = "AUTHORIZED", "Успешный двухстадийный платеж"

    status = models.CharField(
        max_length=100,
        choices=TransactionStatuses.choices,
        default=TransactionStatuses.in_progress,
        verbose_name="Статус",
    )
    partner = models.ForeignKey(
        Partner,
        related_name="tinkoff_transactions",
        verbose_name="Партнер",
        on_delete=models.PROTECT,
    )
