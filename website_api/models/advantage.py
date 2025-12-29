from django.db import models


class Advantage(models.Model):
    """Преимущества платформы"""
    
    TARGET_AUDIENCE_CHOICES = [
        ('client', 'Клиент'),
        ('partner', 'Партнер'),
        ('both', 'Оба'),
    ]
    
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        verbose_name="Целевая аудитория"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    icon_name = models.CharField(
        max_length=50,
        verbose_name="Название иконки"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )

    class Meta:
        db_table = "advantage"
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['target_audience', 'is_active']),
        ]

    def __str__(self):
        return self.title

