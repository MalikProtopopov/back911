from django.db import models

from general_layout.models.abs_review import ReviewAbs
from src.tasks.partner_tasks import update_partner_rating


class Review(ReviewAbs):

    class Meta:
        db_table = "review_db"
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    client = models.ForeignKey(
        "Client",
        related_name="reviews",
        on_delete=models.PROTECT,
        verbose_name="Клиент, оставивший отзыв",
    )
    partner = models.ForeignKey(
        "Partner",
        related_name="reviews",
        on_delete=models.PROTECT,
        verbose_name="Партнер, о котором оставили отзыв",
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        update_partner_rating.delay(self.partner_id)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        update_partner_rating.delay(self.partner_id)
