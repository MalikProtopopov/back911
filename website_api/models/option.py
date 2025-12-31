from django.db import models


class Option(models.Model):
    """Опция услуги"""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Название опции"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Услуга"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Подробное описание опции для пользователя"
    )
    has_parameters = models.BooleanField(
        default=False,
        verbose_name="Есть параметры",
        help_text="Если True, цена зависит от выбранных параметров. "
                  "Если False, используется фиксированная цена из OptionPrice."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    class Meta:
        db_table = "option"
        verbose_name = "Опция"
        verbose_name_plural = "Опции"

    def __str__(self):
        return f"{self.title} ({self.service.title})"
    
    @property
    def required_parameter_types(self):
        """Возвращает типы параметров, которые требуются для этой опции"""
        return [
            link.parameter_type 
            for link in self.parameter_types.filter(is_required=True)
        ]

