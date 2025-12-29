from django.db import models


class CarBrandListAbs(models.Model):
    """Список брендов для выбора"""

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=100,
        verbose_name="Название бренда",
    )
    cyrillic_title = models.CharField(
        max_length=150,
        verbose_name="Название бренда на кириллице",
    )


class CarModelListAbs(models.Model):
    """Список моделей авто для выбора"""

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=100,
        verbose_name="Название бренда",
    )
    cyrillic_title = models.CharField(
        max_length=150,
        verbose_name="Название бренда на кириллице",
    )
