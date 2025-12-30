from django.db import models


class ParameterValue(models.Model):
    """
    Значение параметра.
    
    Примеры:
    - parameter_type='tire_radius', value='R15', display_name='R15'
    - parameter_type='oil_type', value='synthetic_5w40', display_name='Синтетика 5W-40'
    - parameter_type='fuel_type', value='ai92', display_name='АИ-92'
    """
    
    parameter_type = models.ForeignKey(
        'ParameterType',
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name="Тип параметра"
    )
    value = models.CharField(
        max_length=100,
        verbose_name="Значение",
        help_text="Техническое значение, например: R15, synthetic_5w40"
    )
    display_name = models.CharField(
        max_length=150,
        verbose_name="Отображаемое название",
        help_text="Название для пользователя, например: 'R15', 'Синтетика 5W-40'"
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )

    class Meta:
        db_table = "parameter_value"
        verbose_name = "Значение параметра"
        verbose_name_plural = "Значения параметров"
        ordering = ['parameter_type', 'sort_order']
        unique_together = ['parameter_type', 'value']

    def __str__(self):
        return f"{self.parameter_type.title}: {self.display_name}"

