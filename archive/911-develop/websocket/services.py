from typing import Dict, Any, List
from django.core.exceptions import ObjectDoesNotExist

from src.models import Order
from src.services.exceptions import custom_error
from websocket.models.chat import ChatRoom, ChatMessage


def validate_order_status_change_for_client(
    current_status: str, new_status: str
) -> None:
    if current_status in [
        Order.OrderStatuses.new,
        Order.OrderStatuses.on_the_way,
        Order.OrderStatuses.in_progress,
    ] and new_status not in [Order.OrderStatuses.cancelled]:
        raise custom_error("Неверная смена статуса")
    if current_status in [Order.OrderStatuses.on_confirmation] and new_status not in [
        Order.OrderStatuses.cancelled,
        Order.OrderStatuses.done,
    ]:
        raise custom_error("Неверная смена статуса")
    if current_status in [
        Order.OrderStatuses.cancelled,
        Order.OrderStatuses.done,
    ]:
        raise custom_error("Неверная смена статуса")


def validate_order_status_change_for_partner(
    current_status: str, new_status: str
) -> None:
    if current_status in [Order.OrderStatuses.new] and new_status not in [
        Order.OrderStatuses.on_the_way
    ]:
        raise custom_error("Неверная смена статуса")
    if current_status in [Order.OrderStatuses.on_the_way] and new_status not in [
        Order.OrderStatuses.in_progress
    ]:
        raise custom_error("Неверная смена статуса")
    if current_status in [Order.OrderStatuses.in_progress] and new_status not in [
        Order.OrderStatuses.on_confirmation
    ]:
        raise custom_error("Неверная смена статуса")
    if current_status in [
        Order.OrderStatuses.on_confirmation,
        Order.OrderStatuses.cancelled,
        Order.OrderStatuses.done,
    ]:
        raise custom_error("Неверная смена статуса")


def get_chat_history(order_id: int) -> Dict[str, Any]:
    try:
        chat_room = ChatRoom.objects.get(order_id=order_id)
    except ChatRoom.DoesNotExist:
        raise ObjectDoesNotExist("Чат для данного заказа не найден")

    messages = (
        ChatMessage.objects.filter(
            chat_room__order_id=order_id,
        )
        .order_by("-created_at")
        .select_related("chat_room__order", "author")
    )

    total_count = messages.count()

    return {
        "order_id": order_id,
        "messages": messages,
        "total_count": total_count,
    }
