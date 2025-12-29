from django.db import models


class OptionPrice(models.Model):
    """Цена опции в конкретном городе для конкретной категории техники"""
    
    option = models.ForeignKey(
        'Option',
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name="Опция"
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='option_prices',
        verbose_name="Город"
    )
    technic_category = models.ForeignKey(
        'TechnicCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='option_prices',
        verbose_name="Категория техники"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Цена"
    )

    class Meta:
        db_table = "option_price"
        verbose_name = "Цена опции"
        verbose_name_plural = "Цены опций"
        unique_together = ['option', 'city', 'technic_category']
        indexes = [
            models.Index(fields=['option', 'city']),
        ]

    def __str__(self):
        tech_cat = f" ({self.technic_category.title})" if self.technic_category else ""
        return f"{self.option.title} в {self.city.title}{tech_cat}: {self.amount} руб."

