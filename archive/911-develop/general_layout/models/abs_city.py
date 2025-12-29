from django.db import models


class CityAbs(models.Model):
    """Город"""

    class Meta:
        abstract = True

    title = models.CharField(max_length=100, verbose_name="Название города")
