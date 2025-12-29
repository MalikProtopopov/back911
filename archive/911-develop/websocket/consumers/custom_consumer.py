import json

from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import CustomUser
from websocket.consumers.db_sync_to_async import get_user_from_token


class CustomConsumer(AsyncWebsocketConsumer):
    """
    General WebSocket methods
    """

    def __init__(self):
        super().__init__()
        self.user = None
        self.aud = None
        self.auth = None

    async def as_print(self, some_for_print):
        print(some_for_print)

    async def connect(self):
        """
        Handles WebSocket connection and authentication
        """
        try:
            await self.user_auth(self.scope["query_string"].decode("utf-8")[1:])
        except Exception as e:
            await self.accept()
            await self.send(
                text_data=json.dumps(
                    {"error_message": "Invalid token"}, ensure_ascii=False
                )
            )
            await self.close(code=3500)

    async def user_auth(self, token: str):
        """
        Authenticate user based on the provided token
        """
        self.user, self.aud = await get_user_from_token(token)
        if isinstance(self.user, CustomUser):
            self.auth = True
        else:
            raise Exception("Authentication failed")

    async def disconnect_user(self, event):
        await self.close()
