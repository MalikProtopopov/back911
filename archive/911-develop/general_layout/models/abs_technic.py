from django.db import models


class TechnicAbs(models.Model):
    """Авто клиента"""

    class Meta:
        abstract = True

    brand = models.CharField(max_length=100, verbose_name="Марка автомобиля")
    car_model = models.CharField(max_length=100, verbose_name="Модель автомобиля")


class TechnicCategoryAbs(models.Model):
    """Категория автомобиля клиента"""

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=100,
        verbose_name="Название категории",
    )
