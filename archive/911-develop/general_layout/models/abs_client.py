from django.db import models


class ClientAbs(models.Model):
    """Клиент"""

    class ClientStatuses(models.TextChoices):
        active = "active", "Активен"
        blocked = "blocked", "Заблокирован"

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Имя"
    )
    client_status = models.CharField(
        choices=ClientStatuses.choices,
        default=ClientStatuses.active,
        verbose_name="Статус клиента",
    )
