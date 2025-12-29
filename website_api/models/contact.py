from django.db import models


class Contact(models.Model):
    """Контактная информация"""
    
    contact_type = models.CharField(
        max_length=50,
        verbose_name="Тип контакта",
        help_text="phone, email, telegram, whatsapp, vk, instagram и т.д."
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Значение"
    )
    label = models.CharField(
        max_length=255,
        verbose_name="Метка"
    )
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Название иконки"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )

    class Meta:
        db_table = "contact"
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['contact_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.label}: {self.value}"

