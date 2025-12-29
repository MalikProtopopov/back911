from django.db import models


class AppLink(models.Model):
    """Ссылки на приложения в магазинах"""
    
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]
    
    APP_TYPE_CHOICES = [
        ('client', 'Клиент'),
        ('partner', 'Партнер'),
    ]
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name="Платформа"
    )
    app_type = models.CharField(
        max_length=20,
        choices=APP_TYPE_CHOICES,
        verbose_name="Тип приложения"
    )
    store_url = models.CharField(
        max_length=255,
        verbose_name="URL в магазине"
    )
    qr_code_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="URL QR-кода"
    )
    version = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Версия"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    class Meta:
        db_table = "app_link"
        verbose_name = "Ссылка на приложение"
        verbose_name_plural = "Ссылки на приложения"
        unique_together = ['platform', 'app_type']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.get_app_type_display()}"

