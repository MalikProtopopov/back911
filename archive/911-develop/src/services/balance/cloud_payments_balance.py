from datetime import datetime
from decimal import Decimal

import requests
from requests.auth import HTTPBasicAuth

from config import settings
from src.models import Partner
from src.models.cloud_payments import CloudPaymentsTransaction
from src.services.balance.common import PaymentApiService
from src.services.exceptions import custom_error


class CloudPaymentsApiService(PaymentApiService):

    def __init__(
        self,
        pay_amount: Decimal,
        partner: Partner,
    ):
        self.username = settings.CLOUD_PAYMENTS_USERNAME
        self.password = settings.CLOUD_PAYMENTS_PASSWORD
        self.pay_amount = round(float(pay_amount))
        self.pay_decimal = pay_amount
        self.partner = partner
        self.order_id = self._create_order_id()
        self.create_payment_url = "https://api.cloudpayments.ru/orders/create"
        self.currency = "RUB"

    def _create_order_id(self) -> str:
        return f"{self.partner.pk}__{str(datetime.now())[:-7]}"

    def _create_payment_json(self) -> dict:
        payment_json = {
            "Amount": self.pay_amount,
            "Currency": self.currency,
            "Description": "Пополнение баланса",
        }
        return payment_json

    def _create_headers(self):
        return HTTPBasicAuth(
            username=self.username,
            password=self.password,
        )

    def _send_request_to_payment_gateway(self):
        request = requests.post(
            url=self.create_payment_url,
            data=self._create_payment_json(),
            auth=self._create_headers(),
        )
        if request:
            return request.json()
        raise custom_error("Wrong request data", 433)

    def _create_transaction(
        self,
        balance_type: str,
    ) -> str:
        payment = self._send_request_to_payment_gateway()
        try:
            if payment["Success"] and not payment["ErrorCode"]:
                CloudPaymentsTransaction.objects.create(
                    partner=self.partner,
                    payment_id=payment["Model"]["Number"],
                    payment_url=payment["Model"]["Url"],
                    amount=self.pay_decimal,
                    order_id=self.order_id,
                    balance_type=balance_type,
                )
                return payment["Model"]["Url"]
            else:
                raise custom_error(
                    "Failure. Cloud payments error response",
                    433,
                )
        except KeyError:
            raise custom_error(
                "Wrong response from Cloud payments gateway",
                433,
            )

    def create_payment(
        self,
        balance_type: str,
        payment_method: str = "default",
    ) -> str:
        return self._create_transaction(balance_type=balance_type)
