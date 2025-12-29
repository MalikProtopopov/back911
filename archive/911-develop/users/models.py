from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from src.models.administrator import Admin
from src.models.client import Client
from src.models.partner import Partner
from users.managers import CustomUserManager
from users.services.validation.model_validators import validate_charfield_for_letters


class CustomUser(AbstractBaseUser):

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=["-phone"]),
        ]

    phone = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_charfield_for_letters],
        null=True,
        blank=True,
        verbose_name="Номер телефона",
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    client = models.OneToOneField(
        Client,
        null=True,
        blank=True,
        related_name="current_user",
        on_delete=models.SET_NULL,
        db_index=True,
        verbose_name="Клиент",
    )
    partner = models.OneToOneField(
        Partner,
        null=True,
        blank=True,
        related_name="current_user",
        on_delete=models.SET_NULL,
        db_index=True,
        verbose_name="Партнер",
    )
    admin = models.OneToOneField(
        Admin,
        null=True,
        blank=True,
        related_name="current_user",
        on_delete=models.SET_NULL,
        db_index=True,
        verbose_name="Админ",
    )
    is_admin = models.BooleanField(verbose_name="Админ", default=False)
    is_superuser = models.BooleanField(verbose_name="Суперпользователь", default=False)
    is_staff = models.BooleanField(verbose_name="Персонал", default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        if self.phone:
            return self.phone
        return "Нет номера"
