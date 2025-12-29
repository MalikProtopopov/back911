import hashlib
from datetime import datetime
from decimal import Decimal

import requests
from django.conf import settings

from src.models import Partner
from src.models.tinkoff import TinkoffTransaction
from src.services.balance.common import PaymentApiService
from src.services.exceptions import custom_error


class TinkoffApi(PaymentApiService):

    tinkoff_api_url = "https://securepay.tinkoff.ru/v2/"
    headers = {"Content-type": "application/json;charset=utf-8"}
    description = "Пополнение баланса."
    wh_route = "/api/src/balance/tinkoff/"
    crypto_sign = ...  # TODO

    def __init__(
        self,
        pay_amount: Decimal,
        partner: Partner,
    ) -> None:
        self.terminal_key = settings.TINKOFF_TERMINAL_KEY
        self.password = settings.TINKOFF_TOKEN
        self.csrf = settings.CSRF_TRUSTED_ORIGINS
        self.pay_amount = round(float(pay_amount)) * 100
        self.pay_decimal = pay_amount
        self.partner = partner
        self.init_url = f"{self.tinkoff_api_url}Init"
        self.order_id = self._create_order_id()

    def _create_order_id(self) -> str:
        return f"{self.partner.pk}__{str(datetime.now())[:-7]}"

    def _create_payment_json(self) -> dict[str, str | float]:
        self.token = self._create_token()
        self.receipt = self._create_receipt()
        result: dict[str, str | float] = {
            "TerminalKey": self.terminal_key,
            "Amount": str(self.pay_amount),
            "OrderId": self.order_id,
            "Token": self.token,
            "Receipt": self.receipt,
        }
        return result

    def _create_receipt(self):
        result = {
            "Phone": f"+79640245529",
            "Taxation": "osn",
            "Items": [
                {
                    "Name": "Пополнение баланса",
                    "Price": self.pay_amount,
                    "Quantity": 1,
                    "Amount": self.pay_amount,
                    "Tax": "vat10",
                }
            ],
        }
        return result

    def _create_token(self) -> str:
        token_data = [
            {"Amount": str(self.pay_amount)},
            {"OrderId": self.order_id},
            {"Password": self.password},
            {"TerminalKey": self.terminal_key},
        ]
        concat_data: str = ""
        for i in token_data:
            concat_data += str(list(i.values())[0])
        return self._str_to_hash(concat_data)

    def _str_to_hash(self, some_text: str) -> str:
        text_utf8 = some_text.encode("utf-8")
        sha256_hash = hashlib.sha256(text_utf8).hexdigest()
        return sha256_hash

    def _make_payment_gateway(self) -> dict:
        """
        Создать шлюз на платеж
        """
        tinkoff_request = requests.post(
            url=self.init_url,
            headers=self.headers,
            json=self._create_payment_json(),
        )
        if tinkoff_request:
            return tinkoff_request.json()
        else:
            raise custom_error("tinkoff requests error")

    def _create_transaction(self, balance_type: str) -> str:
        """
        Создание транзакции
        """
        payment = self._make_payment_gateway()
        try:
            if payment["Success"] and payment["ErrorCode"] == "0":
                TinkoffTransaction.objects.create(
                    partner=self.partner,
                    payment_id=payment["PaymentId"],
                    payment_url=payment["PaymentURL"],
                    amount=self.pay_decimal,
                    order_id=self.order_id,
                    payment_token=self.token,
                    balance_type=balance_type,
                )
                return payment["PaymentURL"]
            else:
                raise custom_error(
                    "not success response from tinkoff payment gateway",
                    433,
                )
        except KeyError:
            raise custom_error(
                "Error response from tinkoff payment gateway",
                433,
            )

    def create_payment(
        self,
        balance_type: str,
        payment_method: str = "default",
    ) -> str:
        return self._create_transaction(balance_type=balance_type)
