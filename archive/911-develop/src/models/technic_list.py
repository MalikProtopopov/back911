from django.db import models

from general_layout.models.abs_technic_list import CarBrandListAbs, CarModelListAbs


class CarBrandList(CarBrandListAbs):

    class Meta:
        db_table = "car_brand_list_db"
        verbose_name = "Список брендов"
        verbose_name_plural = "Список брендов"

    id = models.CharField(
        primary_key=True,
        editable=True,
        max_length=100,
    )

    def __str__(self):
        return f"{self.title}"


class CarModelList(CarModelListAbs):

    class Meta:
        db_table = "car_model_list_db"
        verbose_name = "Список брендов"
        verbose_name_plural = "Список брендов"

    id = models.CharField(
        primary_key=True,
        editable=True,
        max_length=100,
    )
    brand = models.ForeignKey(
        "CarBrandList",
        related_name="models",
        on_delete=models.CASCADE,
        verbose_name="Бренд автомобиля",
    )
