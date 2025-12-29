from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class ReviewAbs(models.Model):
    """Отзыв"""

    class Meta:
        abstract = True

    comment = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Текст отзыва"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата, время создания отзыва"
    )
