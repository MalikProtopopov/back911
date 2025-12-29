from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from src.models.tinkoff import TinkoffTransaction
from src.tasks.balance_tasks import (
    webhook_handling_tinkoff,
    webhook_handling_cloud_payments,
)


class BalanceViewSet(viewsets.ViewSet):
    queryset = TinkoffTransaction.objects.all()

    @extend_schema(
        summary="Tinkoff web hook",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="tinkoff",
        permission_classes=[AllowAny],
    )
    def tinkoff_webhook(
        self,
        request: Request,
    ) -> Response:
        if isinstance(request.data, dict):
            webhook_handling_tinkoff.delay(request.data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Tinkoff web hook",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="cloud-payments",
        permission_classes=[AllowAny],
    )
    def cloud_payments_webhook(
        self,
        request: Request,
    ) -> Response:
        self.request: Request
        if isinstance(request.data, dict):
            result = webhook_handling_cloud_payments.delay(self.request.data)
            response = result.get()
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
