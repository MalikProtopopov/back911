from django.db import models


class DeliveryZone(models.Model):
    """
    Зона доставки с ценой выезда.
    
    location_status определяет тип зоны:
    - 'in_city' — в городе (обычно бесплатно или дешевле)
    - 'out_city' — за городом (дороже)
    """
    
    LOCATION_CHOICES = [
        ('in_city', 'В городе'),
        ('out_city', 'За городом'),
    ]
    
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='delivery_zones',
        verbose_name="Город"
    )
    zone_name = models.CharField(
        max_length=100,
        verbose_name="Название зоны",
        help_text="Например: 'В городе', 'За городом', 'Пригород'"
    )
    location_status = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        verbose_name="Статус зоны"
    )
    delivery_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена выезда"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    class Meta:
        db_table = "delivery_zone"
        verbose_name = "Зона доставки"
        verbose_name_plural = "Зоны доставки"
        unique_together = ['city', 'location_status']

    def __str__(self):
        return f"{self.city.title} — {self.zone_name}: {self.delivery_price} ₽"

