from django.db import models


class Option(models.Model):
    """Опция услуги"""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Название опции"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Услуга"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    class Meta:
        db_table = "option"
        verbose_name = "Опция"
        verbose_name_plural = "Опции"

    def __str__(self):
        return f"{self.title} ({self.service.title})"

