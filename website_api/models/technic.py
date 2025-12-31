from django.db import models


class TechnicCategory(models.Model):
    """Категория техники (легковой, грузовой и т.д.)"""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Название категории"
    )
    slug = models.SlugField(
        max_length=100,
        blank=True,
        verbose_name="Slug",
        help_text="URL-friendly идентификатор"
    )

    class Meta:
        db_table = "technic_category"
        verbose_name = "Категория техники"
        verbose_name_plural = "Категории техники"

    def __str__(self):
        return self.title

