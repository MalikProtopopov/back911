from django.db import models

from general_layout.models.abs_fcmtoken import FCMTokenAbs


class FCMToken(FCMTokenAbs):

    class Meta:
        db_table = "fcmtoken_db"
        verbose_name = "FCM-токен"
        verbose_name_plural = "FCM-токены"

    client = models.ForeignKey(
        "Client",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fcm_tokens",
        verbose_name="Клиент",
    )
    partner = models.ForeignKey(
        "Partner",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fcm_tokens",
        verbose_name="Партнер",
    )
