from rest_framework import serializers

from src.models.balance import DepositMinimum
from src.models.partner import Partner
from src.serializers.city_serializer import CitySimpleSerializer
from src.serializers.service_serializer import (
    PartnerServiceSerializer,
)
from src.services.partner.partner_orm import check_options_before_city_change
from users.models import CustomUser


class PartnerSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partner
        fields = ["id", "first_name", "last_name"]
        read_only_fields = ["first_name", "last_name"]
        extra_kwargs = {"id": {"read_only": False, "required": False}}


class PartnerSimplePhotoSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(source="current_user.phone")

    class Meta:
        model = Partner
        fields = ["id", "first_name", "rating", "photo", "phone"]


class PartnerProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=20, source="current_user.phone", read_only=True
    )
    city = CitySimpleSerializer(required=False)

    class Meta:
        model = Partner
        fields: list[str] = [
            "id",
            "phone",
            "first_name",
            "last_name",
            "city",
            "legal_status",
            "photo",
            "commission_balance",
            "rating",
            "profit",
        ]
        read_only_fields: list[str] = ["id", "phone", "commission_balance", "profit"]

    def update(self, instance, validated_data):
        if "city" in validated_data:
            city_data = validated_data.pop("city")
        else:
            city_data = None
        if city_data:
            city_id = city_data.get("id")
            check_options_before_city_change(partner_id=instance.id, city_id=city_id)
            instance.city_id = city_id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PartnersForClientAppSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=20, source="current_user.phone", read_only=True
    )
    city = CitySimpleSerializer(required=False)

    class Meta:
        model = Partner
        fields: list[str] = [
            "id",
            "phone",
            "first_name",
            "last_name",
            "city",
            "legal_status",
            "photo",
            "commission_balance",
            "rating",
        ]
        read_only_fields: list[str] = ["id", "phone", "commission_balance"]


class PartnerListOnConfirmationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="current_user.phone")
    datetime_created = serializers.DateTimeField(source="current_user.datetime_created")
    city = CitySimpleSerializer()
    is_deposit = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields: list[str] = [
            "id",
            "phone",
            "photo",
            "first_name",
            "last_name",
            "city",
            "datetime_created",
            "is_deposit",
        ]

    def get_is_deposit(self, obj):
        deposit_minimum = DepositMinimum.objects.first()
        if not deposit_minimum:
            raise serializers.ValidationError(
                {"message": "Депозит не внесен в админке"}
            )
        if obj.deposit_balance >= deposit_minimum.amount:
            return True
        return False


class PartnerListAdminSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="current_user.phone")
    datetime_created = serializers.CharField(source="current_user.datetime_created")
    city = CitySimpleSerializer()
    accepted_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()

    class Meta:
        model = Partner
        fields: list[str] = [
            "id",
            "first_name",
            "last_name",
            "verify",
            "rating",
            "photo",
            "city",
            "phone",
            "datetime_created",
            "is_working",
            "accepted_orders",
            "cancelled_orders",
            "profit",
        ]


class PartnerInfoForAdminSerializer(PartnerListAdminSerializer):
    services = PartnerServiceSerializer(many=True, read_only=True)

    class Meta(PartnerListAdminSerializer.Meta):
        model = Partner
        fields: list[str] = PartnerListAdminSerializer.Meta.fields + [
            "services",
            "legal_status",
            "date_confirmed",
            "deposit_balance",
            "commission_balance",
            "commission_percent",
            "driver_licence",
        ]


class ChangeIsWorkingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partner
        fields: list[str] = ["id", "is_working"]


class PartnerSimplePhoneAndPhotoSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="current_user.phone", read_only=True)

    class Meta:
        model = Partner
        fields = ["id", "first_name", "last_name", "phone", "photo"]


class CreateOrUpdatePartnerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(source="current_user.phone", required=True)

    class Meta:
        model = Partner
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
            "phone",
            "legal_status",
            "city",
            "verify",
            "commission_percent",
        ]

    def create(self, validated_data):
        current_user = validated_data.pop("current_user")
        phone = current_user.get("phone")
        user = CustomUser.objects.filter(phone=phone).first()
        if not user:
            user = CustomUser.objects.create_user(phone=phone)
        partner = Partner.objects.create(**validated_data)
        user.partner = partner
        user.full_clean()
        user.save()
        return partner

    def update(self, instance, validated_data):
        deposit_minimum = DepositMinimum.objects.filter(pk=1).first()
        verify_status = validated_data.get("verify")
        if deposit_minimum and verify_status == Partner.VerifyPartnerStatuses.confirmed:
            instance.deposit_balance = deposit_minimum.amount
        new_user = validated_data.pop("current_user", None)
        if new_user:
            new_phone = new_user.get("phone")
            if instance.current_user.phone != new_phone:
                instance.current_user.phone = new_phone
                instance.current_user.full_clean()
                instance.current_user.save()

        return super().update(instance, validated_data)
