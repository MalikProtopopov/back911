from django.db import models

from general_layout.models.abs_working_zone import WorkingZoneAbs


class WorkingZone(WorkingZoneAbs):

    class Meta:
        db_table = "working_zone_db"
        verbose_name = "Рабочая зона"
        verbose_name_plural = "Рабочие зоны"

    city = models.ForeignKey(
        "City",
        related_name="working_zones",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Город",
    )

    def __str__(self):
        return f"{self.title} в {self.city}"
