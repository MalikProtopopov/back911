from django.db import models


class Lead(models.Model):
    """Заявки с сайта"""
    
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processing', 'В обработке'),
        ('converted', 'Конвертирована'),
        ('rejected', 'Отклонена'),
    ]
    
    LEAD_TYPE_CHOICES = [
        ('service', 'Заявка по услуге от клиента'),
        ('feedback', 'Заявка с предложениями или обратной связью'),
        ('partnership', 'Заявка на партнерство'),
    ]
    
    # Данные клиента
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    
    # Что интересует
    city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name="Город"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name="Услуга"
    )
    message = models.TextField(
        blank=True,
        verbose_name="Сообщение"
    )
    
    # Тип заявки
    lead_type = models.CharField(
        max_length=20,
        choices=LEAD_TYPE_CHOICES,
        default='service',
        verbose_name="Тип заявки"
    )
    
    # UTM метки и информация о странице
    page_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL страницы с которой создана заявка"
    )
    source_page = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Страница источник"
    )
    utm_source = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="UTM Source"
    )
    utm_medium = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="UTM Medium"
    )
    utm_campaign = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="UTM Campaign"
    )
    
    # Статус обработки
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата обработки"
    )

    class Meta:
        db_table = "lead"
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['city', '-created_at']),
            models.Index(fields=['service', '-created_at']),
            models.Index(fields=['lead_type', '-created_at']),
        ]

    def __str__(self):
        return f"Заявка от {self.name} ({self.phone}) - {self.get_lead_type_display()} - {self.get_status_display()}"

