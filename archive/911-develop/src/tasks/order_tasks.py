from celery import shared_task

from src.models.fcmtoken import FCMToken


@shared_task
def send_new_order_ws_notification(order_id: int) -> None:
    from websocket.consumers.order_consumer import OrderConsumer

    """
    Отправляет уведомление при создании заказа
    """
    ws_obj = OrderConsumer()
    ws_obj.handle_notify_partners(order_id)


@shared_task
def get_suitable_partner_tokens(order_id: int) -> list:
    from src.models.order import Order
    from src.services.partner.partner_orm import get_suitable_partner_ids

    order = Order.objects.filter(id=order_id).first()
    if not order:
        return []

    order_options = order.options.values_list("id", flat=True).prefetch_related(
        "options"
    )
    order_service_id = order.service_id
    order_city_id = order.city_id
    order_technic_category_id = (
        order.technic_category_id if order.technic_category_id else None
    )

    suitable_partner_ids = get_suitable_partner_ids(
        options=order_options,
        service_id=order_service_id,
        city_id=order_city_id,
        technic_category_id=order_technic_category_id,
        order_commission=order.commission,
    )
    if not suitable_partner_ids:
        return []

    tokens = FCMToken.objects.filter(partner_id__in=suitable_partner_ids).values_list(
        "token", flat=True
    )
    return list(tokens)


@shared_task
def get_order_member_tokens_task(**kwargs) -> list[str]:
    tokens = FCMToken.objects.filter(**kwargs).values_list("token", flat=True)

    return list(tokens)
