from django.db import transaction
from rest_framework import serializers

from src.models import Service, WorkingZone, City
from src.serializers.city_serializer import CitySimpleSerializer


class CoordinatesInputSerializer(serializers.Serializer):
    coordinates = serializers.ListField(
        min_length=2,
        max_length=2,
        child=serializers.FloatField(),
    )
    service_id = serializers.IntegerField()

    def validate_service_id(self, value):
        service_ids = Service.objects.values_list("id", flat=True)
        if value in service_ids:
            return value
        raise serializers.ValidationError("Выбранная услуга не существует")


class WorkingZoneFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(".geojson"):
            raise serializers.ValidationError(
                "Неверный формат файла. Ожидается geojson."
            )
        return value


class WorkingZoneReadOnlySerializer(serializers.ModelSerializer):

    city = CitySimpleSerializer()

    class Meta:
        model = WorkingZone
        fields = [
            "id",
            "title",
            "departure_price",
            "fuel_delivery_price",
            "location_status",
            "city",
        ]


class WorkingZoneCreateCityAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingZone
        fields = [
            "id",
            "title",
            "departure_price",
            "fuel_delivery_price",
            "location_status",
        ]
        extra_kwargs = {
            "id": {"read_only": False, "required": False},
            "departure_price": {"required": True},
            "fuel_delivery_price": {"required": True},
            "location_status": {"required": True},
        }
        read_only_fields = ["title"]


class CityForAdminSerializer(serializers.ModelSerializer):

    working_zones = WorkingZoneCreateCityAdminSerializer(
        many=True,
        required=True,
    )

    class Meta:
        model = City
        fields = ["id", "title", "working_zones"]

    @transaction.atomic
    def create(self, validated_data):
        working_zones = validated_data.pop("working_zones", [])
        city = City.objects.create(**validated_data)

        for zone in working_zones:
            zone_instance = WorkingZone.objects.filter(id=zone.get("id")).first()
            if zone_instance:
                if zone_instance.city_id:
                    raise serializers.ValidationError(
                        {
                            "error_message": "Выбранные вами зоны уже используются в другом городе"
                        }
                    )
                zone_serializer = WorkingZoneCreateCityAdminSerializer(
                    zone_instance,
                    data=zone,
                    partial=self.partial,
                )
                zone_serializer.is_valid(raise_exception=True)
                zone_serializer.save(city=city)

        return city

    def update(self, instance, validated_data):
        working_zones = validated_data.pop("working_zones", [])
        for zone in working_zones:
            zone_instance = WorkingZone.objects.filter(id=zone.get("id")).first()
            if zone_instance:
                if zone_instance.city_id and zone_instance.city_id != instance.id:
                    raise serializers.ValidationError(
                        {
                            "error_message": "Выбранные вами зоны уже используются в другом городе"
                        }
                    )
                zone_serializer = WorkingZoneCreateCityAdminSerializer(
                    zone_instance,
                    data=zone,
                    partial=self.partial,
                )
                zone_serializer.is_valid(raise_exception=True)
                zone_serializer.save(city=instance)

        return instance
