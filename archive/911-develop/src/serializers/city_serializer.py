from rest_framework import serializers

from src.models.city import City


class CitySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ["id", "title"]
        extra_kwargs = {"id": {"read_only": False, "required": False}}
        read_only_fields = ["title"]


class CityListAdminSerializer(CitySimpleSerializer):

    order_count = serializers.IntegerField()
    partner_count = serializers.IntegerField()
    partners_profit_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    class Meta(CitySimpleSerializer.Meta):
        model = City
        fields = CitySimpleSerializer.Meta.fields + [
            "order_count",
            "partner_count",
            "partners_profit_amount",
        ]
