from django.db import models


class PriceChangeLog(models.Model):
    """
    Лог изменений цен для аудита.
    
    Записывается автоматически при изменении цен через админку.
    """
    
    ENTITY_TYPES = [
        ('OPTION_PRICE', 'Цена опции'),
        ('PARAMETER_PRICE', 'Цена параметра'),
        ('DELIVERY_ZONE', 'Зона доставки'),
    ]
    
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPES,
        verbose_name="Тип сущности"
    )
    entity_id = models.IntegerField(
        verbose_name="ID сущности"
    )
    entity_description = models.CharField(
        max_length=255,
        verbose_name="Описание сущности",
        help_text="Читаемое описание, что изменилось"
    )
    old_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старое значение"
    )
    new_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Новое значение"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата изменения"
    )
    changed_by = models.CharField(
        max_length=150,
        verbose_name="Изменил",
        help_text="Email или имя пользователя"
    )
    reason = models.TextField(
        blank=True,
        verbose_name="Причина изменения"
    )

    class Meta:
        db_table = "price_change_log"
        verbose_name = "Лог изменения цены"
        verbose_name_plural = "Логи изменений цен"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['changed_at']),
        ]

    def __str__(self):
        return f"{self.entity_description}: {self.old_value} → {self.new_value} ({self.changed_at})"

