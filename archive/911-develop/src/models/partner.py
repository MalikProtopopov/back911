from django.db import models

from general_layout.models.abs_partner import PartnerAbs


class Partner(PartnerAbs):

    class Meta:
        db_table = "partner_db"
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"

    city = models.ForeignKey(
        "City",
        related_name="partners",
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Город работы",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
