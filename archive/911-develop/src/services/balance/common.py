from abc import ABC, abstractmethod
from decimal import Decimal

from src.models import Partner


class PaymentApiService(ABC):
    """
    Интерфейс работы с платежными системами.
    Пополнение.
    """

    @abstractmethod
    def create_payment(
        self,
        balance_type: str,
        payment_method: str = "default",
    ) -> str:
        """
        Пополнить баланс
        """


class BalanceService(ABC):
    """
    Интерфейс работы с балансом клиента.
    """

    @abstractmethod
    def subtract_commission_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        """
        Списывает сумму с комиссионного баланса.
        """

    @abstractmethod
    def replenish_deposit_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        """
        Пополнить депозитный баланс на сумму - pay_amount.
        """

    @abstractmethod
    def replenish_commission_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        """
        Пополнить комиссионный баланс на сумму - pay_amount.
        """
