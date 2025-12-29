from src.models import Partner, Order
from src.services.balance.tinkoff_balance import BalanceServiceImpl
from src.services.exceptions import custom_error
from src.services.partner.partner_orm import accrue_profit_to_partner


def subtract_commission(partner: Partner, order: Order):
    BalanceServiceImpl().subtract_commission_balance(
        partner=partner,
        pay_amount=order.commission,
    )
    accrue_profit_to_partner(
        partner=partner,
        profit=order.total_price,
    )
