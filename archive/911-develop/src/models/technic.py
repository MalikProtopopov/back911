from django.db import models

from general_layout.models.abs_technic import TechnicAbs, TechnicCategoryAbs


class TechnicCategory(TechnicCategoryAbs):

    class Meta:
        db_table = "technic_category_db"
        verbose_name = "Категория автомобиля"
        verbose_name_plural = "Категории автомобилей"

    def __str__(self):
        return self.title


class Technic(TechnicAbs):

    class Meta:
        db_table = "technic_db"
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    category = models.ForeignKey(
        "TechnicCategory",
        related_name="technics",
        on_delete=models.PROTECT,
        verbose_name="Категория автомобиля",
    )
    client = models.ForeignKey(
        "Client",
        related_name="technics",
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Владелец автомобиля",
    )

    def __str__(self):
        return f"{self.brand} {self.car_model}"
