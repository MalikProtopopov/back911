from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from config.jwt_auth import PartnerJWTAuthentication
from src.models import PartnerService, Order
from src.models.balance import DepositMinimum
from src.models.cloud_payments import CloudPaymentsTransaction
from src.models.partner import Partner
from src.serializers.balance_serializer import CommissionPaymentSerializer
from src.serializers.order_serializer import GetPartnerOrdersSerializer
from src.serializers.partner_serializer import (
    PartnerProfileSerializer,
    ChangeIsWorkingStatusSerializer,
)
from src.serializers.service_serializer import (
    CreateServiceSerializer,
    GetPartnerServiceAndOptionsSerializer,
)
from src.services.balance.cloud_payments_balance import CloudPaymentsApiService
from src.services.filters import order_custom_partner_filter
from src.services.partner.partner_orm import PartnerServiceRepository


class PartnerViewSet(viewsets.ViewSet):
    queryset = Partner.objects.all()

    @extend_schema(
        summary="Услуги партнера",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="partner-services",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def get_partner_services(self, request) -> Response:
        self.request: Request
        partner = self.request.user.partner
        deposit_minimum = DepositMinimum.objects.all().first()
        if not deposit_minimum:
            return Response({"message": "Депозит не внесен в админке"})
        deposit_balance_flag = bool(partner.deposit_balance >= deposit_minimum.amount)
        verify_status = partner.verify
        response = {
            "status": verify_status,
            "deposit_balance_flag": deposit_balance_flag,
            "partner_is_working": partner.is_working,
            "services": [],
        }
        match verify_status:
            case "on_confirmation":
                return Response(response, status=status.HTTP_200_OK)
            case "rejected" | "blocked":
                return Response(response, status=status.HTTP_200_OK)
            case "confirmed":
                queryset = (
                    PartnerService.objects.filter(partner=partner)
                    .select_related("service", "technic_category")
                    .prefetch_related("options")
                )

                serializer = GetPartnerServiceAndOptionsSerializer(
                    queryset,
                    many=True,
                )
                response.update({"services": serializer.data})
                return Response(response, status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Получить профиль партнера",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-partner-profile",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def get_partner_profile(self, request) -> Response:
        self.request: Request
        partner = (
            Partner.objects.filter(current_user=self.request.user)
            .select_related("city")
            .first()
        )
        serializer = PartnerProfileSerializer(partner)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Обновление профиля партнера",
        request=PartnerProfileSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="update-partner-profile",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def update_partner_profile(self, request) -> Response:
        self.request: Request
        partner = (
            Partner.objects.filter(current_user=self.request.user)
            .select_related("city")
            .first()
        )
        serializer = PartnerProfileSerializer(
            partner, data=self.request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создание услуги партнера",
        request=CreateServiceSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-partner-service",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def create_partner_service(self, request) -> Response:
        self.request: Request
        partner = self.request.user.partner
        serializer = CreateServiceSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            partner_service = PartnerServiceRepository(
                partner=partner, **serializer.validated_data
            ).add_service_and_options()
            return Response(
                {"id": partner_service.pk, **serializer.data}, status.HTTP_201_CREATED
            )
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Редактирование услуги партнера",
        request=CreateServiceSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-partner-service",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def update_partner_service(self, request, pk=None):
        """
        pk = PartnerService id
        """
        self.request: Request
        partner = self.request.user.partner
        serializer = CreateServiceSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        partner_service = PartnerService.objects.filter(pk=pk).first()
        if partner_service:
            partner_orm = PartnerServiceRepository(
                partner=partner, **serializer.validated_data
            )
            partner_orm.update_service(partner_service=partner_service)
            return Response(
                {"id": partner_service.pk, **serializer.data}, status.HTTP_200_OK
            )
        return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Изменение рабочего статуса партнера",
        request=ChangeIsWorkingStatusSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="change-partner-working-status",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def change_partner_working_status(self, request):
        self.request: Request
        partner = self.request.user.partner
        serializer = ChangeIsWorkingStatusSerializer(
            partner, data=self.request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить заказы партнера",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-partner-orders",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def get_partner_orders(self, request) -> Response:
        self.request: Request
        partner = self.request.user.partner
        partner_orders = Order.objects.select_related(
            "client", "service", "technic_category"
        ).prefetch_related("options")
        partner_orders = order_custom_partner_filter(
            request=self.request,
            orders=partner_orders,
            partner=partner,
        )

        serializer = GetPartnerOrdersSerializer(partner_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Оплата депозитного баланса",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="deposit-payment",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def create_deposit_payment(self, request: Request) -> Response:
        self.request: Request
        partner = self.request.user.partner
        minimum_deposit = DepositMinimum.objects.first()
        if not minimum_deposit:
            return Response({"message": "Депозит не внесен в админке"})
        if partner.deposit_balance >= minimum_deposit.amount:
            return Response({"message": "Депозитный баланс уже пополнен"})
        pay_amount = minimum_deposit.amount - partner.deposit_balance
        payment_link = CloudPaymentsApiService(
            pay_amount=pay_amount,
            partner=partner,
        ).create_payment(
            balance_type=CloudPaymentsTransaction.BalanceTypes.deposit_balance,
        )
        return Response({"link": payment_link})

    @extend_schema(
        summary="Оплата комиссионного баланса",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="commission-payment",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def create_commission_payment(self, request: Request) -> Response:
        self.request: Request
        partner = self.request.user.partner
        serializer = CommissionPaymentSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        payment_link = CloudPaymentsApiService(
            pay_amount=serializer.validated_data.get("pay_amount"),
            partner=partner,
        ).create_payment(
            balance_type=CloudPaymentsTransaction.BalanceTypes.commission_balance,
        )
        return Response({"link": payment_link})
