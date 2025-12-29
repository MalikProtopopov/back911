from django.db import models


class SeoMeta(models.Model):
    """SEO метаданные для страниц сайта"""
    
    page_type = models.CharField(
        max_length=50,
        verbose_name="Тип страницы",
        help_text="home, city, service, city_service, about, contacts"
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='seo_metas',
        verbose_name="Город"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='seo_metas',
        verbose_name="Услуга"
    )
    
    # SEO поля
    title = models.CharField(
        max_length=255,
        verbose_name="Title"
    )
    meta_description = models.TextField(
        verbose_name="Meta Description"
    )
    meta_keywords = models.TextField(
        blank=True,
        verbose_name="Meta Keywords"
    )
    h1_title = models.CharField(
        max_length=255,
        verbose_name="H1 заголовок"
    )
    full_slug = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Полный slug"
    )
    
    # Open Graph
    og_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="OG Title"
    )
    og_description = models.TextField(
        blank=True,
        verbose_name="OG Description"
    )
    og_image_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="OG Image URL"
    )
    
    # Schema.org
    schema_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Schema.org JSON"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
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
        db_table = "seo_meta"
        verbose_name = "SEO метаданные"
        verbose_name_plural = "SEO метаданные"
        unique_together = ['page_type', 'city', 'service']
        indexes = [
            models.Index(fields=['full_slug']),
            models.Index(fields=['page_type', 'is_active']),
        ]

    def __str__(self):
        return f"SEO для {self.page_type}: {self.full_slug}"

