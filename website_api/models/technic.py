from django.db import models


class TechnicCategory(models.Model):
    """Категория техники (легковой, внедорожник и т.д.)"""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Название категории"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        related_name='technic_categories',
        verbose_name="Услуга"
    )

    class Meta:
        db_table = "technic_category"
        verbose_name = "Категория техники"
        verbose_name_plural = "Категории техники"

    def __str__(self):
        return f"{self.title} ({self.service.title})"

