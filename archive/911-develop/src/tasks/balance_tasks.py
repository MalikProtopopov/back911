from celery import shared_task

from src.models.cloud_payments import CloudPaymentsTransaction
from src.models.tinkoff import TinkoffTransaction
from src.services.balance.tinkoff_balance import BalanceServiceImpl


@shared_task
def webhook_handling_tinkoff(wh_data: dict) -> None:
    transaction = TinkoffTransaction.objects.filter(
        payment_id=wh_data["PaymentId"]
    ).first()
    if transaction:
        if transaction.status in ["AUTHORIZED", "CONFIRMED"]:
            return
        transaction.status = wh_data["Status"]
        transaction.webhook_data.update(wh_data)
        transaction.save()
    if transaction and transaction.status in ["AUTHORIZED", "CONFIRMED"]:
        if (
            transaction.balance_type
            == TinkoffTransaction.BalanceTypes.commission_balance
        ):
            BalanceServiceImpl().replenish_commission_balance(
                partner=transaction.partner,
                pay_amount=transaction.amount,
            )
        else:
            BalanceServiceImpl().replenish_deposit_balance(
                partner=transaction.partner,
                pay_amount=transaction.amount,
            )


@shared_task
def webhook_handling_cloud_payments(webhook_data: dict) -> dict[str, int] | None:
    if webhook_data["Status"] == "Declined":
        return {"code": 0}
    transaction = CloudPaymentsTransaction.objects.filter(
        payment_id=webhook_data["InvoiceId"]
    ).first()
    if transaction:
        if transaction.status in [
            CloudPaymentsTransaction.TransactionStatuses.confirmed,
            CloudPaymentsTransaction.TransactionStatuses.authorized,
        ]:
            return
        transaction.status = webhook_data["Status"]
        transaction.webhook_data.update(webhook_data)
        transaction.save()
    if transaction and transaction.status in [
        CloudPaymentsTransaction.TransactionStatuses.confirmed,
        CloudPaymentsTransaction.TransactionStatuses.authorized,
    ]:
        if (
            transaction.balance_type
            == TinkoffTransaction.BalanceTypes.commission_balance
        ):
            BalanceServiceImpl().replenish_commission_balance(
                partner=transaction.partner,
                pay_amount=transaction.amount,
            )
        else:
            BalanceServiceImpl().replenish_deposit_balance(
                partner=transaction.partner,
                pay_amount=transaction.amount,
            )

        return {"code": 0}
