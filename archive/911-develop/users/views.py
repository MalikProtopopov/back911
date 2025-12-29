from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from config.jwt_auth import PartnerJWTAuthentication
from users.models import CustomUser
from users.serializers import (
    LoginSerializer,
    CodeVerifySerializer,
    PartnerRegistrationSerializer,
    AdminLoginSerializer,
)
from users.services.admin_auth import AdminAuth
from users.services.user_auth import UserAuth

CODE_ATTEMPTS = 3


class LoginRegisterViewSet(viewsets.ViewSet):
    """Авторизация / регистрация"""

    queryset = CustomUser.objects.all()
    serializer = LoginSerializer

    @extend_schema(
        summary="Отправка кода клиенту / партнеру",
        request=LoginSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="login",
    )
    def send_code_for_user_login(self, request):
        self.request: Request
        serializer = self.serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            phone = serializer.validated_data.get("phone")
            UserAuth(phone).cache_code()
            return Response({"success": True}, status.HTTP_200_OK)
        return Response({"success": False}, status.HTTP_200_OK)

    @extend_schema(
        summary="Логин админа",
        request=AdminLoginSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="admin-login",
    )
    def admin_login_register(self, request) -> Response:
        """Авторизация / регистрация админа"""
        self.request: Request
        serializer = AdminLoginSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            user_login = serializer.validated_data.get("user_login", None)
            password = serializer.validated_data.get("password", None)
            return AdminAuth(user_login).login_admin(password)
        return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Верификация кода",
        request=CodeVerifySerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="verify-code",
    )
    def verify_code(self, request, pk=None) -> Response:
        """Верификация кода"""
        self.request: Request
        if pk not in ["client", "partner"]:
            raise NotFound
        serializer = CodeVerifySerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            phone = serializer.validated_data.get("phone", None)
            code = serializer.validated_data.get("code", None)
            if phone and code:
                return UserAuth(phone).check_code(code=code, user_type=pk)
        return Response(
            {
                "success": False,
            },
            status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Регистрация партнера",
        request=PartnerRegistrationSerializer,
        responses={201: status.HTTP_201_CREATED, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="partner-additional-register",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def partner_register_additional(self, request) -> Response:
        """Доп регистрация для партнера"""
        self.request: Request
        phone = self.request.user.phone
        serializer = PartnerRegistrationSerializer(
            data=self.request.data, context={"phone": phone}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "success": True,
                },
                status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
            },
            status.HTTP_400_BAD_REQUEST,
        )
