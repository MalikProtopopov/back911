from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.models.administrator import Admin
from users.models import CustomUser


def check_phone_for_change_by_admin(phone: str, current_user: CustomUser) -> None:
    user = CustomUser.objects.filter(phone=phone).first()
    if user:
        if user.phone != current_user.phone:
            raise serializers.ValidationError(
                {
                    "error_message": "Пользователь с таким номером телефона уже существует"
                }
            )


class AdminORM:
    def __init__(self, user_login: str, first_name: str | None, role: Admin.AdminRoles):
        self.user_login = user_login
        self.first_name = first_name
        self.role = role

    def get_admin(self) -> Admin:
        return Admin.objects.filter(user_login=self.user_login).first()

    def create_admin(self) -> Admin:
        if self.get_admin():
            raise ValidationError({"error_message": "Такой админ уже существует"})
        admin = Admin.objects.create(
            first_name=self.first_name,
            user_login=self.user_login,
            role=self.role,
        )
        if admin:
            return admin
        raise ValidationError({"error_message": "Некорректные данные"})


class UserAdminORM:
    def __init__(self, phone: str | None, password: str):
        self.phone = phone
        self.password = password

    def get_user(self) -> CustomUser | None:
        user = CustomUser.objects.filter(phone=self.phone).first()
        return user

    def create_new_superuser(self, admin: Admin) -> CustomUser:
        user = CustomUser.objects.create_superuser(
            phone=self.phone,
            password=self.password,
        )
        if user:
            user.admin = admin
            user.save()
            return user
        raise ValidationError({"error_message": "Такой пользователь уже существует"})

    def change_user_to_superuser(self, user: CustomUser, admin: Admin) -> None:
        if user.admin or user.is_admin:
            raise ValidationError({"error_message": "Такой админ уже существует"})
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.set_password(self.password)
        user.admin = admin
        user.save()


class AdminCreator:
    def __init__(
        self,
        user_login: str,
        first_name: str | None,
        phone: str | None,
        password: str,
        role: Admin.AdminRoles,
    ):
        self.admin_orm = AdminORM(
            user_login=user_login,
            first_name=first_name,
            role=role,
        )
        self.user_orm = UserAdminORM(phone=phone, password=password)

    @transaction.atomic
    def create_admin_with_user(self) -> Admin:
        admin = self.admin_orm.create_admin()

        if self.user_orm.phone:
            if user := self.user_orm.get_user():
                self.user_orm.change_user_to_superuser(user, admin)
            else:
                self.user_orm.create_new_superuser(admin)

        else:
            self.user_orm.create_new_superuser(admin)

        return admin
