from dataclasses import asdict
from datetime import datetime
from decimal import Decimal

from src.models import Partner
from src.services.balance.common import BalanceService
from src.services.balance.structs import BalanceHistory


class BalanceServiceImpl(BalanceService):
    def subtract_commission_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        balance_type = "commission_balance"
        before = partner.commission_balance
        partner.commission_balance -= pay_amount
        after = partner.commission_balance
        history = BalanceHistory(
            before=str(before),
            after=str(after),
            balance_type=balance_type,
        )
        partner.commission_balance_history.update(
            {str(datetime.now())[:-7]: asdict(history)}
        )
        partner.save()

    def replenish_deposit_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        balance_type = "deposit_balance"
        before = partner.deposit_balance
        partner.deposit_balance += pay_amount
        after = partner.deposit_balance
        history = BalanceHistory(
            str(before),
            str(after),
            balance_type=balance_type,
        )
        partner.deposit_balance_history.update(
            {str(datetime.now())[:-7]: asdict(history)}
        )
        partner.save()

    def replenish_commission_balance(
        self,
        partner: Partner,
        pay_amount: Decimal,
    ) -> None:
        balance_type = "commission_balance"
        before = partner.commission_balance
        partner.commission_balance += pay_amount
        after = partner.commission_balance
        history = BalanceHistory(
            str(before),
            str(after),
            balance_type=balance_type,
        )
        partner.commission_balance_history.update(
            {str(datetime.now())[:-7]: asdict(history)}
        )
        partner.save()
