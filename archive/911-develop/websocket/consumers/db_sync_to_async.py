import os
from decimal import Decimal
from typing import TYPE_CHECKING

import django
from django.db import transaction
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.backends import jwt

from config.settings import SECRET_KEY
from src.models import Order, Partner, PartnerService, PartnerServiceOption, OptionPrice
from src.models.option import OrderOption
from src.services.exceptions import custom_error
from src.services.order.order_orm import subtract_commission
from src.services.partner.partner_orm import (
    get_suitable_partner_ids,
)
from users.models import CustomUser
from websocket.models.chat import ChatMessage, ChatRoom
from websocket.services import (
    validate_order_status_change_for_client,
    validate_order_status_change_for_partner,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

if TYPE_CHECKING:
    from users.models import CustomUser


@database_sync_to_async
def new_message_query(
    user: CustomUser,
    order_id: int,
    message_text: str,
    user_aud: str,
) -> ChatMessage:
    """get message from db"""
    try:
        chat_room = ChatRoom.objects.get(order_id=order_id)
        if user.pk not in [
            chat_room.order.client.current_user.pk,
            chat_room.order.partner.current_user.pk,
        ]:
            raise custom_error("Permission denied")
        message_model = ChatMessage.objects.create(
            author=user,
            content=message_text,
            chat_room=chat_room,
            user_type=user_aud,
        )
        return message_model
    except ObjectDoesNotExist as e:
        raise custom_error("Room does not exist")


@database_sync_to_async
def get_user_from_token(token: str) -> tuple:
    """
    Attempts to find and return a user using the given validated token.
    """
    try:
        if SECRET_KEY:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=["HS256"], audience=["client", "partner"]
            )
            userid = payload["user_id"]
            audience = payload["aud"]
            user = CustomUser.objects.get(pk=userid)
            return user, audience
    except jwt.ExpiredSignatureError as e:
        raise custom_error(
            f"Authentication token has expired {e}",
            401,
        )
    except (jwt.DecodeError, jwt.InvalidTokenError) as e:
        raise custom_error(
            f"Authorization has failed, Please send valid token. {e}", 401
        )
    else:
        raise KeyError("WTF")


@database_sync_to_async
def get_message_history(page: int, order_id: int) -> list[ChatMessage]:
    page_size = 20
    end_index = page * page_size + 1
    if end_index < 0:
        raise custom_error("Неверная страница")
    messages = list(
        ChatMessage.objects.filter(
            chat_room__order_id=order_id,
        )
        .order_by("-created_at")
        .select_related("chat_room__order")
        .values("id", "author", "content", "created_at", "user_type")[:end_index]
    )

    return messages


@database_sync_to_async
def get_order_by_id(order_id: int) -> Order:
    order = Order.objects.filter(id=order_id).first()
    if order:
        return order
    raise custom_error("Wrong order_id")


@database_sync_to_async
def change_order_status(
    order_id: int,
    status: str,
    audience: str,
    user: CustomUser,
) -> dict:
    with transaction.atomic():
        order = Order.objects.select_for_update().filter(pk=order_id).first()
        if not order:
            raise custom_error("Такой заказ не существует")
        if audience == "client":
            if order.client_id != user.client_id:
                raise custom_error("Неверный пользователь")
            validate_order_status_change_for_client(
                current_status=order.status,
                new_status=status,
            )
        elif audience == "partner":
            if order.partner_id != user.partner_id:
                raise custom_error("Неверный пользователь")
            validate_order_status_change_for_partner(
                current_status=order.status, new_status=status
            )
            if status == Order.OrderStatuses.on_confirmation:
                if partner := Partner.objects.filter(id=order.partner_id).first():
                    subtract_commission(partner=partner, order=order)
        else:
            raise custom_error("Invalid audience")
        order.status = status
        order.save()
        return {
            "order": order,
            "partner_commission_balance": (
                str(order.partner.commission_balance) if order.partner else None
            ),
        }


async def partner_has_active_order(user: CustomUser) -> bool:
    active_statuses = ["in_progress", "on_the_way"]
    qs = Order.objects.filter(partner_id=user.partner_id, status__in=active_statuses)
    exists = await qs.aexists()
    return exists


@database_sync_to_async
def add_partner_to_order(user: CustomUser, order_id: int) -> dict:
    with transaction.atomic():
        order = Order.objects.select_for_update().filter(pk=order_id).first()
        if not order:
            raise custom_error("Такой заказ не существует")
        if order.partner_id:
            raise custom_error("Этот заказ уже принят в работу")
        partner = Partner.objects.filter(id=user.partner_id).first()
        order.set_commission_from_percent(commission_percent=partner.commission_percent)
        if partner.commission_balance < order.commission:
            raise
        order.partner_id = user.partner_id
        order.status = Order.OrderStatuses.on_the_way
        order.save()
        return {
            "order": order,
            "client_user_id": order.client.current_user.id,
            "partner_first_name": order.partner.first_name,
            "partner_last_name": order.partner.last_name,
        }


@database_sync_to_async
def get_suitable_partners_for_order(order: Order) -> list[int]:
    """
    Получает всех партнеров с подходящими услугой, опциями
    и т.д для отправки им уведомлений
    """
    order_options = order.options.values_list("id", flat=True).prefetch_related(
        "options"
    )
    order_service_id = order.service_id
    order_city_id = order.city_id
    order_technic_category_id = (
        order.technic_category_id if order.technic_category_id else None
    )

    return list(
        get_suitable_partner_ids(
            options=order_options,
            service_id=order_service_id,
            city_id=order_city_id,
            technic_category_id=order_technic_category_id,
            order_commission=order.commission,
        )
    )


@database_sync_to_async
def get_order_service_and_options(order: Order) -> dict:
    service_id = order.service_id
    service_title = order.service.title
    options = [
        {"id": option.id, "title": option.title} for option in order.options.all()
    ]
    return {
        "service_id": service_id,
        "service_title": service_title,
        "options": options,
    }


@database_sync_to_async
def get_client_channel(client_user_id: int):
    client_channel_name = cache.get(f"general_user_{client_user_id}")
    return client_channel_name


@database_sync_to_async
def get_order_members_channels_for_status_change(order: Order) -> list[str]:
    channels = []
    if order.client:
        client_user_id = order.client.current_user.id
        if client_channel := cache.get(f"general_user_{client_user_id}"):
            channels.append(client_channel)
    if order.partner:
        partner_user_id = order.partner.current_user.id
        if partner_channel := cache.get(f"general_user_{partner_user_id}"):
            channels.append(partner_channel)
    if channels:
        return channels
    raise custom_error("Нет каналов")


def calculate_additional_price(order: Order, prices: list[OptionPrice]) -> Decimal:
    additional_price = Decimal("0")
    conditions = order.conditions
    for price in prices:
        for condition in conditions:
            condition_type = condition.get("condition_type")
            condition_value = condition.get("condition_value")
            if condition_type == "hours":
                additional_price += price.amount * condition_value
            elif condition_type == "radius":
                order_condition = price.order_conditions.filter(
                    title=condition_value
                ).first()
                if order_condition:
                    additional_price += order_condition.additional_price
                else:
                    pass
            elif condition_type in ("volume", "fuel_type"):
                pass
    return additional_price


@database_sync_to_async
def change_order_options(order_id: int, user: CustomUser, options: list[dict]) -> dict:
    with transaction.atomic():
        order = Order.objects.select_for_update().filter(id=order_id).first()
        if not order:
            raise
        if order.status in (Order.OrderStatuses.done, Order.OrderStatuses.cancelled):
            raise
        partner = Partner.objects.filter(id=user.partner_id).first()
        if not partner.id:
            raise
        if order.partner_id != partner.id:
            raise
        if order.technic_category:
            partner_service = PartnerService.objects.filter(
                partner_id=partner.id,
                service_id=order.service_id,
                technic_category_id=order.technic_category_id,
            ).first()
        else:
            partner_service = PartnerService.objects.filter(
                partner_id=partner.id,
                service_id=order.service_id,
                technic_category__isnull=True,
            ).first()
        if not partner_service:
            raise
        partner_options_count = PartnerServiceOption.objects.filter(
            partner_service_id=partner_service.id,
            option_id__in=options,
        ).count()

        option_ids = [opt["id"] for opt in options]
        if partner_options_count != len(option_ids):
            raise
        OrderOption.objects.filter(order_id=order.id).delete()
        new_order_options = [
            OrderOption(
                order_id=order.id,
                option_id=opt["id"],
                quantity=opt.get("quantity", 1),
            )
            for opt in options
        ]
        OrderOption.objects.bulk_create(new_order_options)
        if order.technic_category:
            options_price_qs = OptionPrice.objects.filter(
                option_id__in=option_ids,
                technic_category_id=order.technic_category_id,
                city_id=order.city_id,
            )
        else:
            options_price_qs = OptionPrice.objects.filter(
                option_id__in=option_ids,
                technic_category_id__isnull=True,
                city_id=order.city_id,
            )

        additional_price = calculate_additional_price(
            order=order, prices=options_price_qs
        )

        option_prices_dict = {
            price.option_id: price.amount for price in options_price_qs
        }
        options_price_sum = Decimal("0.00")
        for opt in options:
            option_price = option_prices_dict.get(opt["id"], Decimal("0.00"))
            quantity = opt.get("quantity", 1)
            options_price_sum += option_price * quantity

        order.options_price = options_price_sum + additional_price
        order.total_price = order.delivery_price + order.options_price
        order.set_commission_from_percent(commission_percent=partner.commission_percent)
        order.save()

        return {
            "order_id": order.id,
            "client_user_id": order.client.current_user.id,
        }
