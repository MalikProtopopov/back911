from rest_framework import serializers

from websocket.models.chat import ChatMessage, ChatRoom


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = "__all__"
