from datetime import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class PartnerAbs(models.Model):
    """Партнер"""

    class VerifyPartnerStatuses(models.TextChoices):
        on_confirmation = "on_confirmation", "Ожидает"
        confirmed = "confirmed", "Подтвержден"
        rejected = "rejected", "Отклонен"
        blocked = "blocked", "Заблокирован"

    class LegalStatuses(models.TextChoices):
        legal_entity = "legal_entity", "Юридическое лицо"
        individual = "individual", "Физическое лицо"

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=60,
        verbose_name="Фамилия",
    )
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name="Рейтинг партнера",
    )
    date_confirmed = models.DateField(
        auto_now=True,
        blank=True,
        null=True,
        verbose_name="Дата подтверждения партнера",
    )
    legal_status = models.CharField(
        choices=LegalStatuses.choices,
        verbose_name="Юридический статус партнера",
    )
    is_working = models.BooleanField(
        default=False,
        verbose_name="В процессе работы",
    )
    photo = models.FileField(
        upload_to=f"uploads/partners/{str(datetime.now())[:-7]}",
        null=True,
        blank=True,
        verbose_name="Фото партнера",
    )
    profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Доход партнера",
    )
    verify = models.CharField(
        max_length=50,
        choices=VerifyPartnerStatuses.choices,
        default=VerifyPartnerStatuses.on_confirmation,
        verbose_name="Верификация партнера",
    )
    commission_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Комиссионный баланс",
    )
    commission_percent = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Процент комиссии",
    )
    deposit_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Депозитный баланс",
    )
    deposit_balance_history = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="История баланса",
    )
    commission_balance_history = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="История баланса",
    )
    driver_licence = models.FileField(
        upload_to=f"uploads/partners/driver_licences/{str(datetime.now())[:-7]}",
        null=True,
        blank=True,
        verbose_name="Водительские права партнера",
    )
