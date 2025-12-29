from rest_framework import serializers

from src.models import TechnicCategory, OptionPrice
from src.models.service import Service, PartnerService
from src.serializers.city_serializer import CitySimpleSerializer
from src.serializers.option_serializer import (
    OptionSimpleSerializer,
    OptionPriceWithoutCitySerializer,
)
from src.serializers.technic_serializer import TechnicCategorySerializer


class ServiceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "title"]
        extra_kwargs = {"id": {"read_only": False, "required": False}}
        read_only_fields = ["title"]


class CreateServiceSerializer(serializers.Serializer):

    service_id = serializers.IntegerField(required=True)
    options_list = serializers.ListSerializer(
        child=serializers.IntegerField(), required=True
    )
    technic_category_id = serializers.IntegerField(allow_null=True, required=False)

    def validate_service_id(self, value):
        services = Service.objects.values_list("id", flat=True)
        if value in services:
            return value
        raise serializers.ValidationError("Выбранной услуги не существует")

    def validate_technic_category_id(self, value: int) -> int | None:
        technic_categories = TechnicCategory.objects.values_list("id", flat=True)
        if value in technic_categories or value is None:
            return value
        raise serializers.ValidationError("Выбранной категории техники не существует")


class PartnerServiceSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer()
    technic_category = TechnicCategorySerializer(read_only=True)
    options = OptionSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = PartnerService
        fields = ["id", "options", "service", "verify_status", "technic_category"]


class ServiceListAdminSerializer(serializers.ModelSerializer):
    partner_id = serializers.IntegerField(source="partner.id")
    photo = serializers.FileField(source="partner.photo")
    phone = serializers.CharField(source="partner.current_user.phone")
    first_name = serializers.CharField(source="partner.first_name")
    last_name = serializers.CharField(source="partner.last_name")
    city = CitySimpleSerializer(source="partner.city")
    service = ServiceSimpleSerializer()
    options = OptionSimpleSerializer(many=True)
    technic_category = TechnicCategorySerializer()

    class Meta:
        model = PartnerService
        fields = [
            "id",
            "partner_id",
            "photo",
            "phone",
            "first_name",
            "last_name",
            "city",
            "service",
            "options",
            "technic_category",
            "verify_status",
        ]


class UpdateServiceVerifyStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerService
        fields = ["id", "verify_status"]

    def update(self, instance, validated_data):
        instance.verify_status = validated_data.get(
            "verify_status", instance.verify_status
        )
        instance.save()
        return instance


class GetPartnerServiceAndOptionsSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer()
    service_status = serializers.CharField(source="verify_status")
    technic_category = TechnicCategorySerializer()
    options = OptionSimpleSerializer(many=True)

    class Meta:
        model = PartnerService
        fields: list[str] = [
            "id",
            "service",
            "service_status",
            "technic_category",
            "options",
        ]


class ServiceForAdminSerializer(serializers.ModelSerializer):

    cities_count = serializers.IntegerField(default=0)
    partners_count = serializers.IntegerField(default=0)
    options = OptionSimpleSerializer(many=True)

    class Meta:
        model = Service
        fields: list[str] = ["options", "cities_count", "partners_count"]


class ServiceWithOptionPricesSerializer(serializers.ModelSerializer):
    option_prices = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields: list[str] = ["id", "title", "option_prices"]

    def get_option_prices(self, obj):
        city = self.context.get("city")
        option_prices = (
            OptionPrice.objects.filter(option__service=obj, city=city)
            .select_related(
                "option__service",
                "technic_category",
            )
            .prefetch_related("order_conditions")
        )
        return OptionPriceWithoutCitySerializer(option_prices, many=True).data
