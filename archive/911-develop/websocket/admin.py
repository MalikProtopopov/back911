from django.contrib import admin

from websocket.models.chat import ChatMessage, ChatRoom

admin.site.register(
    [
        ChatRoom,
        ChatMessage,
    ]
)
