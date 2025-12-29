from django.db import models


class MobileAppVersion(models.Model):

    class Meta:
        db_table = "mobile_app_versions_db"
        verbose_name = "Версии мобильных приложений"
        verbose_name_plural = "Версии мобильных приложений"

    ios_partner = models.TextField(
        max_length=100,
        verbose_name="Версия iOS партнерского приложения",
    )
    android_partner = models.TextField(
        max_length=100,
        verbose_name="Версия Android партнерского приложения",
    )
    ios_client = models.TextField(
        max_length=100,
        verbose_name="Версия iOS клиентского приложения",
    )
    android_client = models.TextField(
        max_length=100,
        verbose_name="Версия Android клиентского приложения",
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super(MobileAppVersion, self).save(*args, **kwargs)
