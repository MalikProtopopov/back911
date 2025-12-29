from django.db import models
from slugify import slugify as russian_slugify


class Service(models.Model):
    """Модель услуги"""
    
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название услуги"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL slug"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        db_table = "service"
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['display_order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = russian_slugify(self.title)
        super().save(*args, **kwargs)

