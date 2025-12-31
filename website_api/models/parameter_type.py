from django.db import models


class ParameterType(models.Model):
    """
    Динамический тип параметра.
    
    Примеры:
    - code='tire_radius', title='Радиус шины'
    - code='oil_type', title='Тип масла'
    - code='fuel_type', title='Тип топлива'
    - code='boom_height', title='Высота автовышки'
    - code='distance', title='Расстояние эвакуации'
    
    Вы можете добавлять ЛЮБЫЕ типы параметров через админку!
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Код параметра",
        help_text="Уникальный код, например: tire_radius, oil_type, fuel_type"
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Название",
        help_text="Отображаемое название, например: 'Радиус шины', 'Тип масла'"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Подсказка для пользователя при выборе"
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parameter_type"
        verbose_name = "Тип параметра"
        verbose_name_plural = "Типы параметров"
        ordering = ['sort_order', 'title']

    def __str__(self):
        return f"{self.title} ({self.code})"

