from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from config.jwt_auth import ClientOrPartnerJWTAuthentication
from src.models.fcmtoken import FCMToken
from src.serializers.fcmtoken_serializer import FCMTokenSerializer


class FCMTokenViewSet(viewsets.ViewSet):
    queryset = FCMToken.objects.all()
    serializer_class = FCMTokenSerializer

    @extend_schema(
        summary="Добавление FCM-токена юзеру",
        request=FCMTokenSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="create",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[ClientOrPartnerJWTAuthentication],
    )
    def add_fcm_token_to_user(self, request, pk=None):
        self.request: Request
        match pk:
            case "client":
                serializer = FCMTokenSerializer(
                    data=self.request.data,
                    context={"user_id": self.request.user.client_id, "user_type": pk},
                )
            case "partner":
                serializer = FCMTokenSerializer(
                    data=self.request.data,
                    context={"user_id": self.request.user.partner_id, "user_type": pk},
                )
            case _:
                raise NotFound

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)
