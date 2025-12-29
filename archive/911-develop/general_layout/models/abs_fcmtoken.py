from django.db import models


class FCMTokenAbs(models.Model):
    """FCM-токен"""

    class Meta:
        abstract = True

    token = models.CharField(max_length=255, verbose_name="FCM-токен")
    device_id = models.CharField(max_length=255, verbose_name="ID устройства")
