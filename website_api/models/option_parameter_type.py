from django.db import models


class OptionParameterType(models.Model):
    """
    Связь опции с типом параметра.
    Определяет какие параметры нужны для расчета цены опции.
    
    Примеры:
    - Опция "Замена колеса" требует параметр "tire_radius"
    - Опция "Замена масла" требует параметр "oil_type"
    - Опция "Эвакуатор" — не требует параметров (фиксированная цена)
    """
    
    option = models.ForeignKey(
        'Option',
        on_delete=models.CASCADE,
        related_name='parameter_types',
        verbose_name="Опция"
    )
    parameter_type = models.ForeignKey(
        'ParameterType',
        on_delete=models.CASCADE,
        related_name='option_links',
        verbose_name="Тип параметра"
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательный",
        help_text="Если True, пользователь обязан выбрать значение этого параметра"
    )

    class Meta:
        db_table = "option_parameter_type"
        verbose_name = "Параметр опции"
        verbose_name_plural = "Параметры опций"
        unique_together = ['option', 'parameter_type']

    def __str__(self):
        return f"{self.option.title} → {self.parameter_type.title}"

