import random

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from src.models import Client
from src.tasks.sms_tasks import send_sms
from users.dataclasses import CodeAuthData
from users.models import CustomUser


class UserAuth:
    def __init__(self, phone: str) -> None:
        self.phone = phone

    def get_user(self) -> CustomUser | None:
        """Получить пользователя"""
        user = CustomUser.objects.filter(phone=self.phone).first()
        if user:
            return user
        else:
            return None

    def _create_user(self) -> CustomUser:
        """Создать пользователя"""
        new_user = CustomUser.objects.create_user(self.phone)
        if new_user:
            return new_user
        raise ValidationError("Введите корректный номер телефона!")

    @transaction.atomic
    def _create_user_and_client(self) -> CustomUser:
        """Создать клиента"""
        user = self._create_user()
        client = Client.objects.create()
        user.client = client
        user.save()
        return user

    def _create_code(self) -> int:
        """Создать смс-код"""
        verify_code = 1234
        google_phone = "0000000000"
        if settings.DEBUG == "True" or self.phone == google_phone:
            return verify_code
        verify_code = random.randint(1000, 9999)
        send_sms.delay(self.phone, str(verify_code))
        return verify_code

    def _cache_set(self, code_data: CodeAuthData) -> None:
        """Добавить в кэш"""
        cache.set(self.phone, code_data)

    def cache_code(self, attempt_counter=3) -> None:
        """Добавить смс-код в кэш"""
        data_for_cache = CodeAuthData(
            code=self._create_code(), attempt_counter=attempt_counter
        )
        self._cache_set(data_for_cache)

    def _get_cache(self) -> CodeAuthData:
        """Достать из кэша"""
        result = cache.get(self.phone)
        if result:
            return result
        raise AuthenticationFailed

    def check_code(self, code: int, user_type: str) -> Response:
        code_data = self._get_cache()
        if code == code_data.code:
            return self.login_register(user_type)
        else:
            return self._respond_to_wrong_code(code_data.attempt_counter)
        return self.login_register(user_type)

    def _activate_inactive_user(self, user: CustomUser) -> None:
        """Активировать неактивного пользователя"""
        if not user.is_active:
            user.is_active = True

    def _create_token(self, user: CustomUser, user_type: str) -> dict:
        refresh = RefreshToken.for_user(user)
        refresh["aud"] = user_type
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "is_new": False if user_type == "client" else (not bool(user.partner)),
            "is_active": user.is_active,
        }

    def _check_for_client_instance(self, user: CustomUser):
        """
        Если юзер сначала зарегистрировался как партнер,
        то у него не создается объект клиента
        Эта функция проверяет и создает объект клиента
        """
        if not user.client:
            client = Client.objects.create()
            user.client = client
            user.save()

    def login(self, user: CustomUser, user_type: str) -> Response:
        self._activate_inactive_user(user)
        if user_type == "client":
            self._check_for_client_instance(user)
        return Response(self._create_token(user, user_type), status.HTTP_200_OK)

    def register_client_or_error(self, user_type: str) -> Response:
        try:
            client = self._create_user_and_client()
            token = self._create_token(client, user_type)
            return Response(token, status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Введите верные учетные данные"},
                status.HTTP_400_BAD_REQUEST,
            )

    def register(self, user_type: str) -> Response:
        if user_type == "client":
            return self.register_client_or_error(user_type)
        return Response(
            self._create_token(self._create_user(), user_type), status.HTTP_201_CREATED
        )

    def login_register(self, user_type: str) -> Response:
        if user := self.get_user():
            return self.login(user, user_type)
        return self.register(user_type)

    def _respond_to_wrong_code(self, attempt_counter: int) -> Response:
        if attempt_counter > 0:
            attempt_counter -= 1
            self.cache_code(attempt_counter)
            return Response(
                {
                    "success": False,
                    "attempts_left": attempt_counter,
                    "message": "Введите код повторно",
                },
                status.HTTP_400_BAD_REQUEST,
            )
        else:
            cache.delete(self.phone)
            return Response(
                {
                    "success": False,
                    "attempts_left": attempt_counter,
                    "message": "Повторите попытку авторизации",
                },
                status.HTTP_400_BAD_REQUEST,
            )
