from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.models.partner import Partner
from users.services.user_auth import UserAuth


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, required=True)

    def validate_phone(self, value):
        acceptable_chars = "0123456789"
        for char in value:
            if char not in acceptable_chars:
                raise serializers.ValidationError("Недопустимое значение!")
        return value


class AdminLoginSerializer(serializers.Serializer):
    user_login = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=50, required=True, write_only=True)


class CodeVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, required=True)
    code = serializers.IntegerField(required=True)


class PartnerRegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=20,
        required=True,
        source="current_user.phone",
    )

    class Meta:
        model = Partner
        fields = [
            "first_name",
            "last_name",
            "legal_status",
            "city",
            "phone",
            "driver_licence",
        ]
        extra_kwargs = {"driver_licence": {"required": True}}

    def validate_phone(self, value) -> str:
        request_phone = self.context["phone"]
        if request_phone != value:
            raise serializers.ValidationError("Телефоны не соответствуют")
        return value

    def create(self, validated_data):
        current_user = validated_data.pop("current_user")
        phone = current_user.get("phone")
        user = UserAuth(phone).get_user()
        if user.partner:
            raise ValidationError(
                {"error_message": "Партнер с таким номером телефона уже существует"}
            )
        new_partner = Partner.objects.create(**validated_data)
        user.partner = new_partner
        user.save()
        return new_partner
