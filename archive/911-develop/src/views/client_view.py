from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from config.jwt_auth import ClientJWTAuthentication
from src.models import Partner, Order
from src.models.client import Client
from src.models.technic import Technic
from src.serializers.client_serializer import ClientProfileSerializer
from src.serializers.order_serializer import (
    CreateOrderSerializer,
    GetClientOrdersSerializer,
)
from src.serializers.partner_serializer import PartnersForClientAppSerializer
from src.serializers.review_serializer import ReviewSerializer
from src.serializers.technic_serializer import TechnicSerializer
from src.services.filters import order_custom_client_filter
from src.services.permissions import IsTechnicOwner


class ClientViewSet(viewsets.ViewSet):
    queryset = Client.objects.all()

    @extend_schema(
        summary="Получение профиля клиента",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-client-profile",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[ClientJWTAuthentication],
    )
    def get_client_profile(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        serializer = ClientProfileSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Обновление профиля клиента",
        request=ClientProfileSerializer,
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="update-client-profile",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[ClientJWTAuthentication],
    )
    def update_client_profile(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        serializer = ClientProfileSerializer(
            client, data=self.request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Добавить новую технику",
        request=TechnicSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-technic",
        permission_classes=[IsAuthenticated, IsTechnicOwner],
        authentication_classes=[ClientJWTAuthentication],
    )
    def add_client_technic(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        serializer = TechnicSerializer(
            data=self.request.data, context={"request": self.request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Изменить существующую технику",
        request=TechnicSerializer,
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-technic",
        permission_classes=[IsAuthenticated, IsTechnicOwner],
        authentication_classes=[ClientJWTAuthentication],
    )
    def update_client_technic(self, request, pk=None) -> Response:
        self.request: Request
        technic = Technic.objects.filter(pk=pk)
        if technic.exists():
            serializer = TechnicSerializer(
                technic.first(), data=self.request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Удалить существующую технику",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-technic",
        permission_classes=[IsAuthenticated, IsTechnicOwner],
        authentication_classes=[ClientJWTAuthentication],
    )
    def delete_client_technic(self, request, pk=None) -> Response:
        technic = Technic.objects.filter(pk=pk)
        if technic.exists():
            technic.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Список партнеров",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-partners",
    )
    def get_list_of_partners(self, request) -> Response:
        partners = Partner.objects.filter(
            verify=Partner.VerifyPartnerStatuses.confirmed
        ).select_related("city", "current_user")
        serializer = PartnersForClientAppSerializer(partners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создать заказ",
        request=CreateOrderSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-order",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def create_order_by_client(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        serializer = CreateOrderSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Получить заказы клиента",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-client-orders",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[ClientJWTAuthentication],
    )
    def get_client_orders(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        client_orders = (
            Order.objects.filter(client=client)
            .select_related("partner")
            .prefetch_related("options", "service")
        )
        client_orders = order_custom_client_filter(
            request=self.request, orders=client_orders
        )

        serializer = GetClientOrdersSerializer(client_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Оставить отзыв о партнере",
        request=ReviewSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="leave-review",
        permission_classes=[IsAuthenticated, IsTechnicOwner],
        authentication_classes=[ClientJWTAuthentication],
    )
    def leave_review(self, request) -> Response:
        self.request: Request
        client = self.request.user.client
        serializer = ReviewSerializer(
            data=self.request.data, context={"client": client}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)
