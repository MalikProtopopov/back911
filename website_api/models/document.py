from django.db import models
from slugify import slugify as russian_slugify


class Document(models.Model):
    """Модель документа для сайта (политика конфиденциальности, оферта и т.д.)"""
    
    # Основные поля
    title = models.CharField(
        max_length=255,
        verbose_name="Название документа"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL slug",
        help_text="Уникальный идентификатор для URL (генерируется автоматически из названия)"
    )
    version = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="Версия документа",
        help_text="Версия документа, например: 1.0, 2.1, v1.2.3"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Неактивные документы не отображаются на сайте"
    )
    
    # Контент (HTML)
    short_description = models.TextField(
        blank=True,
        verbose_name="Краткое описание (HTML)",
        help_text="Краткое описание документа для превью и списков"
    )
    full_description = models.TextField(
        verbose_name="Полное описание (HTML)",
        help_text="Полный текст документа"
    )
    
    # SEO поля
    meta_title = models.CharField(
        max_length=255,
        verbose_name="SEO Title",
        help_text="Заголовок страницы для поисковых систем"
    )
    meta_description = models.TextField(
        verbose_name="SEO Meta Description",
        help_text="Описание страницы для поисковых систем"
    )
    meta_keywords = models.TextField(
        blank=True,
        verbose_name="SEO Meta Keywords",
        help_text="Ключевые слова для поисковых систем (опционально)"
    )
    h1_title = models.CharField(
        max_length=255,
        verbose_name="H1 заголовок",
        help_text="Основной заголовок на странице документа"
    )
    
    # Даты
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        db_table = "document"
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_active', '-updated_at']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = russian_slugify(self.title)
        super().save(*args, **kwargs)

