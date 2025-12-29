import json

from channels.layers import get_channel_layer
from django.core.cache import cache

from src.services.exceptions import custom_error
from websocket.consumers.custom_consumer import CustomConsumer
from websocket.consumers.db_sync_to_async import new_message_query, get_message_history
from websocket.dataclass import ChatMessageData, ChatHistoryData
from websocket.decorator import ws_auth
from websocket.models import ChatMessage


class ChatConsumer(CustomConsumer):
    """ """

    simple_actions = []

    def __init__(self):
        super().__init__()
        self.room = None
        self.entry_json = None

    async def connect(self):
        await super().connect()
        if self.user:
            user_id = self.user.pk
            existing_channel_name = cache.get(f"chat_user_{user_id}")
            if existing_channel_name:
                channel_layer = get_channel_layer()
                await channel_layer.send(
                    existing_channel_name, {"type": "disconnect_user"}
                )
            cache.set(f"chat_user_{user_id}", self.channel_name, timeout=None)
        self.room = f'chat_{self.scope["url_route"]["kwargs"]["room_name"]}'
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    @ws_auth
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_dict: dict = json.loads(text_data)
            await self.convert_entry_json(text_data_dict)
        else:
            await self.disconnect(3500)

    async def convert_entry_json(self, text_data_dict: dict) -> None:
        if text_data_dict["command"] == "new_message":
            self.entry_json = ChatMessageData(**text_data_dict)
        elif text_data_dict["command"] == "get_history":
            self.entry_json = ChatHistoryData(**text_data_dict)
        else:
            raise custom_error("wrong command in ws!", 3500)
        await self.commands[self.entry_json.command](self)

    async def new_message(self) -> None:
        new_message_create = await new_message_query(
            user=self.user,
            order_id=self.scope["url_route"]["kwargs"]["room_name"],
            message_text=self.entry_json.message_text,
            user_aud=self.aud,
        )
        await self.send_to_chat_message(new_message_create)

    async def send_to_chat_message(self, message: ChatMessage) -> None:
        if self.entry_json.command == "new_message" and self.channel_layer:
            await self.channel_layer.group_send(
                self.room,
                {
                    "type": "chat_message",
                    "id": message.id,
                    "content": message.content,
                    "created_at": str(message.created_at),
                    "author": message.author_id,
                    "user_type": message.user_type,
                },
            )

    async def get_history(self):
        messages = await get_message_history(
            order_id=self.scope["url_route"]["kwargs"]["room_name"],
            page=self.entry_json.page,
        )
        for message in messages:
            message["created_at"] = str(message["created_at"])
        await self.channel_layer.group_send(
            self.room,
            {"type": "get_messages", "user_id": self.user.id, "message_data": messages},
        )

    async def disconnect(self, code=None):
        if self.channel_layer and self.user:
            await self.channel_layer.group_discard(self.room, self.channel_name)
        if self.user and self.user.pk:
            cache.delete(f"chat_user_{self.user.pk}")
        await self.close(code)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    async def get_messages(self, event):
        user_id = event["user_id"]
        if self.user.id == user_id:
            await self.send(text_data=json.dumps(event, ensure_ascii=False))

    commands = {
        "new_message": new_message,
        "get_history": get_history,
    }
