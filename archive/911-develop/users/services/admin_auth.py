from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from src.models.administrator import Admin
from users.models import CustomUser


class AdminAuth:
    def __init__(self, user_login: str) -> None:
        self.user_login = user_login

    def _get_admin(self) -> CustomUser | None:
        user = (
            CustomUser.objects.filter(admin__user_login=self.user_login)
            .select_related("admin")
            .first()
        )
        return user

    def _create_admin_token(self, user: CustomUser):
        refresh = RefreshToken.for_user(user)
        refresh["aud"] = "admin"
        data = {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": user.admin.role,
        }
        return data

    def login_admin(self, password: str) -> Response:
        user = self._get_admin()
        if user and user.check_password(password):
            if not hasattr(user, "admin") or not user.admin:
                return Response(
                    {"success": False, "message": "Админ не связан с пользователем"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                self.check_admin_is_active(user)
            except PermissionError as e:
                return Response(
                    {"success": False, "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(self._create_admin_token(user), status=status.HTTP_200_OK)
        return Response(
            {"success": False, "message": "Неверный логин или пароль"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def check_admin_is_active(self, user: CustomUser):
        if user.admin.admin_status == "blocked":
            raise PermissionError("Доступ запрещен")
