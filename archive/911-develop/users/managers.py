from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, phone):
        if not phone:
            raise ValueError("Обязательное поле")

        user = self.model(phone=phone)
        user.set_unusable_password()
        user.full_clean()
        user.save()

        return user

    def create_superuser(self, phone=None, password=None):

        user = self.model(
            phone=phone,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        return user
