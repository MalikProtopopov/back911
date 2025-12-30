from django.db import models


class ParameterPrice(models.Model):
    """
    Модификатор цены для конкретного значения параметра.
    
    Логика:
    - Если опция требует параметр, ищем ParameterPrice
    - Если ParameterPrice найден — используем price_modifier
    - Если не найден — параметр бесплатный (price_modifier = 0)
    
    Примеры:
    - option="Замена колеса", parameter_value="R19", city="Махачкала" → +500 ₽
    - option="Замена масла", parameter_value="Синтетика 5W-40", city="Махачкала" → +300 ₽
    """
    
    option = models.ForeignKey(
        'Option',
        on_delete=models.CASCADE,
        related_name='parameter_prices',
        verbose_name="Опция"
    )
    parameter_value = models.ForeignKey(
        'ParameterValue',
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name="Значение параметра"
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='parameter_prices',
        verbose_name="Город"
    )
    technic_category = models.ForeignKey(
        'TechnicCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parameter_prices',
        verbose_name="Категория техники",
        help_text="Если цена зависит от категории техники"
    )
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Модификатор цены",
        help_text="Надбавка к базовой цене опции"
    )

    class Meta:
        db_table = "parameter_price"
        verbose_name = "Цена параметра"
        verbose_name_plural = "Цены параметров"
        unique_together = ['option', 'parameter_value', 'city', 'technic_category']
        indexes = [
            models.Index(fields=['option', 'city']),
            models.Index(fields=['parameter_value', 'city']),
        ]

    def __str__(self):
        tc = f" ({self.technic_category.title})" if self.technic_category else ""
        return f"{self.option.title} + {self.parameter_value.display_name} в {self.city.title}{tc}: +{self.price_modifier} ₽"

