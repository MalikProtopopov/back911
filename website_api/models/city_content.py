from django.db import models


class CityContent(models.Model):
    """Контент для страницы города на сайте"""
    
    city = models.OneToOneField(
        'City',
        on_delete=models.CASCADE,
        related_name='content',
        verbose_name="Город"
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=255,
        verbose_name="Meta Title"
    )
    meta_description = models.TextField(
        verbose_name="Meta Description"
    )
    h1_title = models.CharField(
        max_length=255,
        verbose_name="Заголовок H1"
    )
    
    # Контент
    short_description = models.TextField(
        verbose_name="Краткое описание"
    )
    full_description = models.TextField(
        verbose_name="Полное описание (HTML)"
    )
    advantages_html = models.TextField(
        blank=True,
        verbose_name="Преимущества (HTML)"
    )
    
    # Кешированная статистика (обновляется через Celery)
    partner_count = models.IntegerField(
        default=0,
        verbose_name="Количество партнеров"
    )
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Средний рейтинг"
    )
    review_count = models.IntegerField(
        default=0,
        verbose_name="Количество отзывов"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        db_table = "city_content"
        verbose_name = "Контент города"
        verbose_name_plural = "Контент городов"

    def __str__(self):
        return f"Контент для {self.city.title}"

