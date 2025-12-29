from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.jwt_auth import ClientOrPartnerJWTAuthentication
from src.models.fcmtoken import FCMToken
from src.serializers.fcmtoken_serializer import FCMTokenSerializer


class InitViewSet(viewsets.ViewSet):
    queryset = FCMToken.objects.all()
    serializer_class = FCMTokenSerializer

    @extend_schema(
        summary="Проверка токена при входе в приложение",
        responses={200: status.HTTP_200_OK, 401: status.HTTP_401_UNAUTHORIZED},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="token",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[ClientOrPartnerJWTAuthentication],
    )
    def check_token(self, request):
        return Response({"success": True}, status.HTTP_200_OK)
