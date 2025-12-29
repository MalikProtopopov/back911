from django.db import models


class AdminAbs(models.Model):
    """Администратор"""

    class AdminStatuses(models.TextChoices):
        active = "active", "Активен"
        blocked = "blocked", "Заблокирован"

    class AdminRoles(models.TextChoices):
        super_admin = "super_admin", "Суперадмин"
        operator = "operator", "Оператор"

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Имя"
    )
    admin_status = models.CharField(
        max_length=25,
        choices=AdminStatuses.choices,
        default=AdminStatuses.active,
        verbose_name="Статус админа",
    )
    user_login = models.CharField(
        max_length=100, unique=True, verbose_name="Логин админа"
    )
    role = models.CharField(
        max_length=20,
        choices=AdminRoles.choices,
        default=AdminRoles.operator,
        verbose_name="Роль",
    )
