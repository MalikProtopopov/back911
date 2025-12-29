from django.db import models


class ServiceContent(models.Model):
    """Контент для страницы услуги на сайте"""
    
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="Услуга"
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='service_contents',
        verbose_name="Город",
        help_text="NULL для общего описания услуги"
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
    description = models.TextField(
        verbose_name="Описание (HTML)"
    )
    how_it_works_html = models.TextField(
        blank=True,
        verbose_name="Как это работает (HTML)"
    )
    benefits_html = models.TextField(
        blank=True,
        verbose_name="Преимущества (HTML)"
    )
    
    # Медиа
    icon_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="URL иконки"
    )
    cover_image_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="URL обложки"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        db_table = "service_content"
        verbose_name = "Контент услуги"
        verbose_name_plural = "Контент услуг"
        unique_together = ['service', 'city']

    def __str__(self):
        city_name = f" в {self.city.title}" if self.city else " (общий)"
        return f"Контент для {self.service.title}{city_name}"

