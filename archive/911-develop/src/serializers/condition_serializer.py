from rest_framework import serializers

from src.models.order import OrderConditions


class OrderConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderConditions
        fields: list[str] = [
            "id",
            "title",
            "condition_type",
            "additional_price",
        ]
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class CreateOrderConditionByAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderConditions
        fields: list[str] = [
            "id",
            "title",
            "condition_type",
        ]
