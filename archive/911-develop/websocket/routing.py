from django.urls import path, re_path

from websocket.consumers.chat_consumer import ChatConsumer
from websocket.consumers.order_consumer import OrderConsumer

websocket_urlpatterns = [
    path("ws/general/", OrderConsumer.as_asgi()),
    re_path(
        r"ws/chat/(?P<room_name>\w+)/$",
        ChatConsumer.as_asgi(),
        name="user_consumer",
    ),
]
