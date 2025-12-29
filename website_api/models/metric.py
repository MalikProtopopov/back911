from django.db import models


class Metric(models.Model):
    """Метрики для отображения на сайте"""
    
    metric_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Ключ метрики"
    )
    value = models.CharField(
        max_length=100,
        verbose_name="Значение"
    )
    display_label = models.CharField(
        max_length=255,
        verbose_name="Отображаемая метка"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    metric_type = models.CharField(
        max_length=50,
        verbose_name="Тип метрики",
        help_text="platform, partner, client, city, service"
    )
    is_visible_on_site = models.BooleanField(
        default=True,
        verbose_name="Показывать на сайте"
    )
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Название иконки"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее обновление"
    )

    class Meta:
        db_table = "metric"
        verbose_name = "Метрика"
        verbose_name_plural = "Метрики"
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['metric_key']),
            models.Index(fields=['is_visible_on_site', 'display_order']),
        ]

    def __str__(self):
        return f"{self.display_label}: {self.value}"

