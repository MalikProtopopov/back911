from rest_framework import serializers

from src.models.client import Client
from src.serializers.order_serializer import OrderSerializer
from src.serializers.technic_serializer import (
    TechnicSerializer,
    TechnicDetailSerializer,
)
from users.models import CustomUser


class ClientSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ["id", "first_name"]
        read_only_fields = ["first_name"]


class ClientNameWithPhoneSimpleSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="current_user.phone", read_only=True)

    class Meta:
        model = Client
        fields = ["id", "first_name", "phone"]


class ClientProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=20, source="current_user.phone", read_only=True
    )
    technics = TechnicSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Client
        fields = ["id", "first_name", "phone", "technics"]


class CreateOrUpdateClientForAdminSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="current_user.phone")

    class Meta:
        model = Client
        fields = ["id", "first_name", "phone", "client_status"]

    def create(self, validated_data):
        user_data = validated_data.pop("current_user")
        current_user = CustomUser.objects.create_user(user_data.get("phone"))
        client = Client.objects.create(**validated_data)
        current_user.client = client
        current_user.save()

        return client

    def update(self, instance, validated_data):
        if "current_user" in validated_data.keys():
            new_user = validated_data.pop("current_user")
            new_phone = new_user.get("phone")
            if instance.current_user.phone != new_phone:
                instance.current_user.phone = new_phone
                instance.current_user.full_clean()
                instance.current_user.save()

        return super().update(instance, validated_data)


class ClientListAdminSerializer(CreateOrUpdateClientForAdminSerializer):
    datetime_created = serializers.CharField(source="current_user.datetime_created")

    class Meta(CreateOrUpdateClientForAdminSerializer.Meta):
        model = Client
        fields = CreateOrUpdateClientForAdminSerializer.Meta.fields + [
            "datetime_created",
        ]


class ClientDetailForAdminSerializer(CreateOrUpdateClientForAdminSerializer):

    technics = TechnicDetailSerializer(many=True, read_only=True)
    orders = OrderSerializer(many=True, read_only=True)

    class Meta(CreateOrUpdateClientForAdminSerializer.Meta):
        model = Client
        fields = CreateOrUpdateClientForAdminSerializer.Meta.fields + [
            "technics",
            "orders",
        ]
