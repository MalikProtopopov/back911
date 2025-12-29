from django.db import models
from django.utils.text import slugify
from slugify import slugify as russian_slugify


class City(models.Model):
    """Модель города"""
    
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название города"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL slug"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        db_table = "city"
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['display_order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'display_order']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = russian_slugify(self.title)
        super().save(*args, **kwargs)

