from django.db import models


class OptionAbs(models.Model):
    """Опция услуги"""

    class Meta:
        abstract = True

    title = models.CharField(max_length=150, unique=True, verbose_name="Название опции")


class ServiceAbs(models.Model):
    """Услуга"""

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=150, unique=True, verbose_name="Название услуги"
    )
