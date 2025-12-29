from decimal import Decimal

from rest_framework import serializers

from src.models import OptionPrice
from src.models.option import Option, PartnerServiceOption, OrderOption
from src.models.order import OrderConditions
from src.serializers.city_serializer import CitySimpleSerializer
from src.serializers.condition_serializer import OrderConditionSerializer
from src.serializers.technic_serializer import (
    TechnicCategorySerializer,
    TechnicCategoryIdProvideSerializer,
)


class OptionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ["id", "title"]
        extra_kwargs = {"id": {"read_only": False, "required": False}}
        read_only_fields = ["title"]


class OrderOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="option.id")
    title = serializers.CharField(source="option.title")
    price = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()
    total = serializers.SerializerMethodField()

    def get_price(self, obj):
        order = self.context.get("order")
        if not order:
            return Decimal("0.00")

        technic_category_id = order.technic_category_id
        city_id = order.city_id
        option_id = obj.option.id

        if technic_category_id:
            option_price = OptionPrice.objects.filter(
                option_id=option_id,
                technic_category_id=technic_category_id,
                city_id=city_id,
            ).first()
        else:
            option_price = OptionPrice.objects.filter(
                option_id=option_id,
                technic_category_id__isnull=True,
                city_id=city_id,
            ).first()

        return option_price.amount if option_price else Decimal("0.00")

    def get_total(self, obj):
        price = self.get_price(obj)
        return price * obj.quantity


class OrderOptionInputSerializer(serializers.Serializer):
    option_id = serializers.IntegerField(required=False, allow_null=True)
    id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(
        default=1,
        required=False,
        min_value=1,
        max_value=10,
        error_messages={
            "invalid": "Количество должно быть целым числом",
            "min_value": "Минимальное количество: 1",
            "max_value": "Максимальное количество: 10",
        },
    )

    def validate(self, attrs):
        option_id_value = attrs.get("option_id", None)
        if not option_id_value:
            option_id_value = attrs.get("id", None)

        if not option_id_value:
            raise serializers.ValidationError(
                {"option_id": "Требуется поле 'id' или 'option_id'"}
            )

        attrs["id"] = option_id_value

        if "option_id" in attrs:
            del attrs["option_id"]

        return attrs


class PartnerServiceOptionSerializer(serializers.ModelSerializer):
    option = OptionSimpleSerializer()

    class Meta:
        model = PartnerServiceOption
        fields = ["option"]


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ["id", "title", "service"]


class OptionPriceSimpleSerializer(serializers.ModelSerializer):
    option = OptionSimpleSerializer()
    order_conditions = OrderConditionSerializer(many=True)

    class Meta:
        model = OptionPrice
        fields = [
            "id",
            "option",
            "amount",
            "order_conditions",
        ]


class OptionPriceWithoutCitySerializer(serializers.ModelSerializer):
    option = OptionSimpleSerializer(required=True)
    technic_category = TechnicCategorySerializer()
    order_conditions = OrderConditionSerializer(many=True)

    class Meta:
        model = OptionPrice
        fields = [
            "id",
            "option",
            "amount",
            "technic_category",
            "order_conditions",
        ]


class OrderConditionForCreateOptionPrice(serializers.Serializer):
    title = serializers.CharField()
    condition_type = serializers.ChoiceField(
        choices=OrderConditions.ConditionTypes.choices,
    )
    additional_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )


class OrderConditionForUpdateOptionPrice(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    condition_type = serializers.ChoiceField(
        choices=OrderConditions.ConditionTypes.choices,
    )
    additional_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )


class CreateOptionPriceSerializer(serializers.Serializer):
    option = serializers.IntegerField()
    technic_category = serializers.IntegerField(allow_null=True)
    city = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    order_conditions = OrderConditionForCreateOptionPrice(
        many=True,
    )

    def validate(self, attrs):
        option_id = attrs.get("option")
        city_id = attrs.get("city")
        technic_category_id = attrs.get("technic_category")

        if OptionPrice.objects.filter(
            option_id=option_id,
            city_id=city_id,
            technic_category_id=technic_category_id,
        ).exists():
            raise serializers.ValidationError(
                {
                    "error_message": "Цена для данной опции, города и категории техники уже существует"
                }
            )
        return attrs


class UpdateOptionPriceSerializer(serializers.Serializer):
    option = serializers.IntegerField()
    technic_category = serializers.IntegerField(allow_null=True)
    city = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    order_conditions_to_create = OrderConditionForCreateOptionPrice(many=True)
    order_conditions_to_update = OrderConditionForUpdateOptionPrice(
        many=True,
    )
    order_conditions_to_delete = serializers.ListField()

    def validate(self, attrs):
        option_id = attrs.get("option")
        city_id = attrs.get("city")
        technic_category_id = attrs.get("technic_category")

        existing = OptionPrice.objects.filter(
            option_id=option_id,
            city_id=city_id,
            technic_category_id=technic_category_id,
        ).exclude(id=self.instance_id)

        if existing.exists():
            raise serializers.ValidationError(
                {
                    "error_message": "Цена для данной опции, города и категории техники уже существует"
                }
            )

        return attrs


class OptionPriceSerializer(serializers.ModelSerializer):

    option = OptionSimpleSerializer()
    technic_category = TechnicCategoryIdProvideSerializer()
    city = CitySimpleSerializer()
    order_conditions = OrderConditionSerializer(many=True)

    class Meta:
        model = OptionPrice
        fields = [
            "id",
            "option",
            "technic_category",
            "city",
            "amount",
            "order_conditions",
        ]
