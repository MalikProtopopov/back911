import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache

from src.services.exceptions import custom_error
from websocket.consumers.custom_consumer import CustomConsumer
from websocket.consumers.db_sync_to_async import (
    change_order_status,
    add_partner_to_order,
    get_suitable_partners_for_order,
    get_client_channel,
    get_order_by_id,
    get_order_service_and_options,
    get_order_members_channels_for_status_change,
    change_order_options,
    partner_has_active_order,
)
from websocket.dataclass import (
    PartnerOrderAddRequest,
    OrderStatusChangeRequest,
    NotifyPartnersRequest,
    ChangeOrderOptionsRequest,
)
from websocket.decorator import ws_auth


class OrderConsumer(CustomConsumer):

    partner_room: str = "partner_room"

    def __init__(self):
        super().__init__()
        self.entry_json = None
        self.order_room = None

    async def connect(self):
        await super().connect()
        if self.user:
            user_id = self.user.pk
            existing_channel_name = cache.get(f"general_user_{user_id}")
            if existing_channel_name:
                channel_layer = get_channel_layer()
                await channel_layer.send(
                    existing_channel_name, {"type": "disconnect_user"}
                )
            cache.set(f"general_user_{user_id}", self.channel_name, timeout=None)
        if self.aud == "partner":
            await self.channel_layer.group_add(self.partner_room, self.channel_name)
            await self.accept()
        elif self.aud == "client":
            await self.accept()
        else:
            await self.disconnect(3500)

    async def disconnect(self, code=None):
        if self.aud == "partner":
            await self.channel_layer.group_discard(self.partner_room, self.channel_name)
            if self.entry_json:
                await self.channel_layer.group_discard(
                    f"order_{self.entry_json.order_id}", self.channel_name
                )
        elif self.aud == "client":
            if self.entry_json:
                await self.channel_layer.group_discard(
                    f"order_{self.entry_json.order_id}", self.channel_name
                )

        if self.user and self.user.pk:
            cache.delete(f"general_user_{self.user.pk}")
        await self.close(code)

    @ws_auth
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_dict: dict = json.loads(text_data)
            await self._parse_command(text_data_dict)
        else:
            await self.disconnect(3500)

    async def _parse_command(self, text_data_dict: dict) -> None:
        match text_data_dict["command"]:
            case "accept_order":
                self.entry_json = PartnerOrderAddRequest(**text_data_dict)
            case "change_order_status":
                self.entry_json = OrderStatusChangeRequest(**text_data_dict)
            case "notify_partners":
                self.entry_json = NotifyPartnersRequest(**text_data_dict)
            case "change_options":
                self.entry_json = ChangeOrderOptionsRequest(**text_data_dict)
            case _:
                raise custom_error("wrong command in ws!", 3500)
        await self.commands[self.entry_json.command](self)

    async def handle_change_order_status(self) -> None:
        try:
            order_data = await change_order_status(
                order_id=self.entry_json.order_id,
                status=self.entry_json.status,
                audience=self.aud,
                user=self.user,
            )
            order = order_data["order"]
            order_channels = await get_order_members_channels_for_status_change(
                order=order
            )
            if order_channels:
                for channel in order_channels:
                    await self.channel_layer.group_add(
                        f"order_{self.entry_json.order_id}", channel
                    )
            await self.channel_layer.group_send(
                f"order_{self.entry_json.order_id}",
                {
                    "type": "change_status",
                    "order_id": order.id,
                    "status": order.status,
                    "partner_commission_balance": order_data[
                        "partner_commission_balance"
                    ],
                },
            )
        except custom_error as e:
            await self.send(
                text_data=json.dumps(
                    {
                        "error": str(e),
                        "code": 400,
                    },
                    ensure_ascii=False,
                    default=str,
                ),
            )

    async def handle_accept_order(self) -> None:
        if self.aud == "partner":
            if await partner_has_active_order(self.user):
                await self.send(
                    text_data=json.dumps(
                        {
                            "error": "You have active order, can't accept new one",
                            "code": 400,
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                )

            elif not await partner_has_active_order(self.user):
                order_data = await add_partner_to_order(
                    order_id=self.entry_json.order_id,
                    user=self.user,
                )
                client_channel_name = await get_client_channel(
                    order_data["client_user_id"]
                )
                if client_channel_name:
                    await self.channel_layer.group_add(
                        f"order_{self.entry_json.order_id}",
                        client_channel_name,
                    )
                suitable_partners = await get_suitable_partners_for_order(
                    order=order_data["order"]
                )
                for room in (self.partner_room, f"order_{self.entry_json.order_id}"):
                    await self.channel_layer.group_send(
                        room,
                        {
                            "type": "accept_order_command",
                            "order_id": order_data["order"].id,
                            "status": order_data["order"].status,
                            "partner": {
                                "id": order_data["order"].partner_id,
                                "first_name": order_data["partner_first_name"],
                                "last_name": order_data["partner_last_name"],
                            },
                            "suitable_partners": suitable_partners,
                        },
                    )
        else:
            raise custom_error("You don't have permission", 3500)

    async def handle_change_order_options(self) -> None:
        if self.aud == "partner":
            entry: ChangeOrderOptionsRequest = self.entry_json
            order_data = await change_order_options(
                order_id=entry.order_id,
                user=self.user,
                options=entry.options,
            )
            client_channel_name = await get_client_channel(order_data["client_user_id"])
            if client_channel_name:
                await self.channel_layer.group_add(
                    f"order_{self.entry_json.order_id}",
                    client_channel_name,
                )
            for room in (self.partner_room, f"order_{self.entry_json.order_id}"):
                await self.channel_layer.group_send(
                    room,
                    {
                        "type": "change_options",
                        "order_id": order_data["order_id"],
                    },
                )
        else:
            raise custom_error("You don't have permission", 3500)

    @async_to_sync
    async def handle_notify_partners(self, order_id: int):
        order = await get_order_by_id(order_id=order_id)
        suitable_partners = await get_suitable_partners_for_order(order=order)
        service_options_data = await get_order_service_and_options(order=order)
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            self.partner_room,
            {
                "type": "notify",
                "order_id": order.id,
                "created_at": str(order.datetime_created),
                "status": order.status,
                "delivery_price": str(order.delivery_price),
                "options_price": str(order.options_price),
                "comment": order.comment,
                "service": {
                    "id": service_options_data["service_id"],
                    "title": service_options_data["service_title"],
                },
                "options": service_options_data["options"],
                "city_id": order.city_id,
                "suitable_partners": suitable_partners,
            },
        )

    async def accept_order_command(self, event):
        send_event = event.copy()
        suitable_partners = send_event.pop("suitable_partners")
        if (
            self.aud == "partner"
            and self.user.partner_id in suitable_partners
            or self.aud == "client"
        ):
            await self.send(text_data=json.dumps(send_event, ensure_ascii=False))

    async def change_status(self, event):
        await self.send(
            text_data=json.dumps(
                event,
                ensure_ascii=False,
            ),
        )

    async def change_options(self, event):
        await self.send(
            text_data=json.dumps(
                event,
                ensure_ascii=False,
            ),
        )

    async def notify(self, event):
        send_event = event.copy()
        suitable_partners = send_event.pop("suitable_partners")
        if self.aud == "partner" and self.user.partner_id in suitable_partners:
            await self.send(
                text_data=json.dumps(
                    send_event,
                    ensure_ascii=False,
                    default=str,
                ),
            )

    commands = {
        "change_order_status": handle_change_order_status,
        "accept_order": handle_accept_order,
        "notify_partners": handle_notify_partners,
        "change_options": handle_change_order_options,
    }
