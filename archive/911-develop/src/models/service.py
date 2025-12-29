from django.db import models

from general_layout.models.abs_service_and_option import ServiceAbs


class Service(ServiceAbs):

    class Meta:
        db_table = "service_db"
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class PartnerService(models.Model):

    class VerifyStatuses(models.TextChoices):
        on_confirmation = "on_confirmation", "Ожидает"
        confirmed = "confirmed", "Подтверждена"
        rejected = "rejected", "Отклонена"

    class Meta:
        db_table = "partner_service_db"
        verbose_name = "Услуга партнера"
        verbose_name_plural = "Услуги партнера"
        constraints = [
            models.UniqueConstraint(
                fields=["service", "partner", "technic_category"],
                name="unique service of partner",
                violation_error_message="Услуга уже существует",
            )
        ]

    service = models.ForeignKey(
        Service,
        db_index=True,
        on_delete=models.PROTECT,
    )
    partner = models.ForeignKey(
        "Partner",
        related_name="services",
        db_index=True,
        on_delete=models.PROTECT,
    )
    technic_category = models.ForeignKey(
        "TechnicCategory",
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.PROTECT,
    )
    options = models.ManyToManyField(
        "Option",
        related_name="services",
        through="PartnerServiceOption",
        verbose_name="Опции партнерской услуги",
    )
    verify_status = models.CharField(
        max_length=50,
        choices=VerifyStatuses.choices,
        default=VerifyStatuses.on_confirmation,
        verbose_name="Верификация услуги",
    )
