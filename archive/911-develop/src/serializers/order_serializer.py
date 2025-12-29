from datetime import datetime
from decimal import Decimal
from django.db import transaction, IntegrityError, InternalError
from rest_framework import serializers

from src.models import Order, Partner, OptionPrice
from src.models.option import OrderOption
from src.models.order import OrderConditions
from src.serializers.city_serializer import CitySimpleSerializer
from src.serializers.option_serializer import (
    OptionSimpleSerializer,
    OrderOptionSerializer,
    OrderOptionInputSerializer,
)
from src.serializers.partner_serializer import (
    PartnerSimplePhoneAndPhotoSerializer,
    PartnerSimplePhotoSerializer,
    PartnerSimpleSerializer,
)
from src.serializers.service_serializer import ServiceSimpleSerializer


class OrderSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer(read_only=True)
    partner = PartnerSimplePhotoSerializer(read_only=True)
    options = OptionSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields: list[str] = ["id", "address", "service", "options", "partner", "status"]


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


class CreateOrderSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer()
    options = serializers.ListField(required=True, allow_empty=False, write_only=True)
    city = CitySimpleSerializer(required=True)
    conditions = serializers.JSONField(required=False, default=list)
    total_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    options_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields: list[str] = [
            "id",
            "point_coordinates",
            "comment",
            "total_price",
            "options_price",
            "delivery_price",
            "address",
            "conditions",
            "service",
            "options",
            "technic_brand_model",
            "city",
            "technic_category",
            "change_history",
        ]

    def validate_options(self, value):
        if not value:
            return value

        normalized_options = []

        for option in value:
            if isinstance(option, dict):
                if "title" in option:
                    normalized_options.append({"id": option["id"], "quantity": 1})
                else:
                    serializer = OrderOptionInputSerializer(data=option)
                    serializer.is_valid(raise_exception=True)
                    normalized_options.append(serializer.validated_data)
            else:
                raise serializers.ValidationError(
                    f"Неверный формат опции. Ожидается объект, получено: {type(option)}"
                )

        return normalized_options

    def extract_related_data(self, validated_data):
        service_id = validated_data.pop("service").get("id")
        city_id = validated_data.pop("city").get("id")

        options_data = validated_data.pop("options")
        options_with_quantity = [
            (option["id"], option.get("quantity", 1)) for option in options_data
        ]

        technic_category = validated_data.pop("technic_category", None)
        technic_category_id = technic_category.id if technic_category else None

        return service_id, city_id, options_with_quantity, technic_category_id

    def _calculate_options_price(
        self, options_with_quantity, technic_category_id, city_id, conditions
    ) -> tuple[Decimal, Decimal]:
        """Расчет стоимости опций и дополнительных платежей"""
        option_ids = [opt_id for opt_id, _ in options_with_quantity]

        if technic_category_id:
            options_price_qs = OptionPrice.objects.filter(
                option_id__in=option_ids,
                technic_category_id=technic_category_id,
                city_id=city_id,
            )
        else:
            options_price_qs = OptionPrice.objects.filter(
                option_id__in=option_ids,
                technic_category_id__isnull=True,
                city_id=city_id,
            )

        additional_price = self._calculate_additional_price(
            conditions, options_price_qs
        )

        option_prices_dict = {
            price.option_id: price.amount for price in options_price_qs
        }

        options_price_sum = Decimal("0.00")
        for option_id, quantity in options_with_quantity:
            option_price = option_prices_dict.get(option_id, Decimal("0.00"))
            options_price_sum += option_price * quantity

        options_price = options_price_sum + additional_price
        return options_price, options_price_sum

    def _calculate_additional_price(self, conditions, prices_qs) -> Decimal:
        """Расчет дополнительной цены на основе условий заказа"""
        additional_price = Decimal("0")
        if not conditions or not isinstance(conditions, list):
            return additional_price

        for price in prices_qs:
            for condition in conditions:
                if isinstance(condition, dict):
                    condition_type = condition.get("condition_type")
                    condition_value = condition.get("condition_value")
                    if condition_type == "hours":
                        additional_price += price.amount * Decimal(str(condition_value))
                    elif condition_type == "radius":
                        order_condition = price.order_conditions.filter(
                            title=condition_value
                        ).first()
                        if order_condition:
                            additional_price += order_condition.additional_price
        return additional_price

    def create(self, validated_data) -> Order:
        service_id, city_id, options_with_quantity, technic_category_id = (
            self.extract_related_data(validated_data)
        )

        delivery_price = validated_data.get("delivery_price", Decimal("0.00"))
        conditions = validated_data.get("conditions", [])

        # Calculate prices
        options_price, options_price_sum = self._calculate_options_price(
            options_with_quantity, technic_category_id, city_id, conditions
        )
        total_price = delivery_price + options_price

        # Set calculated prices
        validated_data["options_price"] = options_price
        validated_data["total_price"] = total_price

        order = Order.objects.create(
            service_id=service_id,
            city_id=city_id,
            technic_category_id=technic_category_id,
            **validated_data,
        )

        for option_id, quantity in options_with_quantity:
            OrderOption.objects.create(
                order=order, option_id=option_id, quantity=quantity
            )

        order_options = OrderOption.objects.filter(order=order).select_related("option")
        options_history = []
        for order_option in order_options:
            options_history.append(
                {
                    "id": order_option.option.id,
                    "title": order_option.option.title,
                    "quantity": order_option.quantity,
                }
            )

        change_history_entry = {
            "timestamp": datetime.now().isoformat(),
            "options": options_history,
            "options_price": float(options_price),
            "total_price": float(total_price),
        }

        order.change_history = {"changes": [change_history_entry]}
        order.save(update_fields=["change_history"])

        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        order_options = OrderOption.objects.filter(order=instance).select_related(
            "option"
        )

        representation["options"] = OrderOptionSerializer(
            order_options, many=True, context={"order": instance}
        ).data

        return representation


class CreateOrderForAdminSerializer(CreateOrderSerializer):
    status = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    options_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta(CreateOrderSerializer.Meta):
        model = Order
        fields = CreateOrderSerializer.Meta.fields + ["client", "partner", "status"]

    def validate_technic_category(self, value):
        if not value:
            raise serializers.ValidationError("Поле 'Категория техники' обязательно")
        return value

    def validate_options(self, value):
        if not value:
            raise serializers.ValidationError("Поле 'Опции' обязательно")
        if len(value) == 0:
            raise serializers.ValidationError("Поле 'Опции' обязательно")

        normalized_options = []

        for option in value:
            if isinstance(option, int):
                normalized_options.append({"id": option, "quantity": 1})
            elif isinstance(option, dict):
                if "title" in option:
                    normalized_options.append({"id": option["id"], "quantity": 1})
                else:
                    serializer = OrderOptionInputSerializer(data=option)
                    serializer.is_valid(raise_exception=True)
                    normalized_options.append(serializer.validated_data)
            else:
                raise serializers.ValidationError(
                    f"Неверный формат опции. Ожидается число или объект, получено: {type(option)}"
                )

        return normalized_options

    def _calculate_additional_price(self, conditions, prices_qs) -> Decimal:
        """Расчет дополнительной цены на основе условий заказа"""
        additional_price = Decimal("0")
        if not conditions or not isinstance(conditions, list):
            return additional_price

        for price in prices_qs:
            for condition in conditions:
                if isinstance(condition, dict):
                    condition_type = condition.get("condition_type")
                    condition_value = condition.get("condition_value")
                    if condition_type == "hours":
                        additional_price += price.amount * Decimal(str(condition_value))
                    elif condition_type == "radius":
                        order_condition = price.order_conditions.filter(
                            title=condition_value
                        ).first()
                        if order_condition:
                            additional_price += order_condition.additional_price
        return additional_price

    def create(self, validated_data) -> Order:
        client = validated_data.pop("client", None)
        partner = validated_data.pop("partner", None)

        # Create order using base class logic (which calculates prices)
        order = super().create(validated_data)

        # Add admin-specific fields
        order.client = client
        order.partner = partner

        # Calculate commission
        if partner:
            commission_percent = partner.commission_percent
            order_commission = round(order.total_price * commission_percent / 100, 2)
            order.commission = round(order_commission, 2)
            order.status = Order.OrderStatuses.on_the_way

        # Save the order with updated fields
        order.save()

        return order

    def update(self, instance: Order, validated_data):
        new_partner: Partner = validated_data.pop("partner", None)
        if new_partner:
            new_partner_id = new_partner.id
        else:
            new_partner_id = None
        instance_partner_id = instance.partner_id

        if not new_partner_id:
            instance.partner_id = new_partner_id
            instance.status = Order.OrderStatuses.new
            instance.commission = Decimal("0")

        if instance_partner_id != new_partner_id:
            instance.partner_id = new_partner_id
            instance.set_commission_from_percent(
                commission_percent=new_partner.commission_percent
            )
            instance.status = Order.OrderStatuses.on_the_way

        # Initialize change_history for existing orders if not exists
        if not instance.change_history:
            order_options = OrderOption.objects.filter(order=instance).select_related(
                "option"
            )
            options_history = []
            for order_option in order_options:
                options_history.append(
                    {
                        "id": order_option.option.id,
                        "title": order_option.option.title,
                        "quantity": order_option.quantity,
                    }
                )

            change_history_entry = {
                "timestamp": (
                    instance.datetime_created.isoformat()
                    if instance.datetime_created
                    else datetime.now().isoformat()
                ),
                "options": options_history,
                "options_price": float(instance.options_price),
                "total_price": float(instance.total_price),
            }

            instance.change_history = {"changes": [change_history_entry]}
            instance.save(update_fields=["change_history"])

        # Обработка связанных полей и отслеживание изменений
        options_changed = False
        options_with_quantity = None

        related_fields = ["service", "city", "options", "technic_category"]
        for field in related_fields:
            value = validated_data.pop(field, None)
            if value:
                if field == "options":
                    options_with_quantity = [
                        (option["id"], option.get("quantity", 1)) for option in value
                    ]
                    OrderOption.objects.filter(order=instance).delete()
                    for option_id, quantity in options_with_quantity:
                        OrderOption.objects.create(
                            order=instance, option_id=option_id, quantity=quantity
                        )
                    options_changed = True
                elif field == "technic_category":
                    setattr(
                        instance,
                        f"{field}_id",
                        value.id if hasattr(value, "id") else value,
                    )
                else:
                    setattr(
                        instance,
                        f"{field}_id",
                        value.get("id", getattr(instance, f"{field}_id")),
                    )

        delivery_price_changed = "delivery_price" in validated_data
        conditions_changed = "conditions" in validated_data

        if options_changed or delivery_price_changed or conditions_changed:
            delivery_price = validated_data.get(
                "delivery_price", instance.delivery_price
            )
            conditions = validated_data.get("conditions", [])

            if options_with_quantity is None:
                order_options = OrderOption.objects.filter(order=instance)
                options_with_quantity = [
                    (oo.option_id, oo.quantity) for oo in order_options
                ]

            option_ids = [opt_id for opt_id, _ in options_with_quantity]

            technic_category_id = getattr(instance, "technic_category_id", None)
            if technic_category_id:
                options_price_qs = OptionPrice.objects.filter(
                    option_id__in=option_ids,
                    technic_category_id=technic_category_id,
                    city_id=instance.city_id,
                )
            else:
                options_price_qs = OptionPrice.objects.filter(
                    option_id__in=option_ids,
                    technic_category_id__isnull=True,
                    city_id=instance.city_id,
                )

            additional_price = self._calculate_additional_price(
                conditions, options_price_qs
            )

            option_prices_dict = {
                price.option_id: price.amount for price in options_price_qs
            }

            options_price_sum = Decimal("0.00")
            for option_id, quantity in options_with_quantity:
                option_price = option_prices_dict.get(option_id, Decimal("0.00"))
                options_price_sum += option_price * quantity

            options_price = options_price_sum + additional_price
            total_price = delivery_price + options_price

            validated_data["options_price"] = options_price
            validated_data["total_price"] = total_price

            if new_partner:
                commission_percent = new_partner.commission_percent
            elif instance.partner:
                commission_percent = instance.partner.commission_percent
            else:
                commission_percent = Decimal("0.00")

            instance.commission = round(total_price * commission_percent / 100, 2)

        # Track options changes in history
        if options_changed:
            # Get current options after changes
            current_order_options = OrderOption.objects.filter(
                order=instance
            ).select_related("option")
            current_options = []
            for order_option in current_order_options:
                current_options.append(
                    {
                        "id": order_option.option.id,
                        "title": order_option.option.title,
                        "quantity": order_option.quantity,
                    }
                )

            # Get previous options from last change history entry
            previous_options = []
            if (
                instance.change_history
                and "changes" in instance.change_history
                and instance.change_history["changes"]
            ):
                last_change = instance.change_history["changes"][-1]
                previous_options = last_change.get("options", [])

            # Compare options (sort both lists for consistent comparison)
            def sort_options(opts):
                return sorted(opts, key=lambda x: (x["id"], x["quantity"]))

            current_sorted = sort_options(current_options)
            previous_sorted = sort_options(previous_options)

            # Only add to history if options actually changed
            if current_sorted != previous_sorted:
                change_history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "options": current_options,
                    "options_price": float(
                        validated_data.get("options_price", instance.options_price)
                    ),
                    "total_price": float(
                        validated_data.get("total_price", instance.total_price)
                    ),
                }

                if not instance.change_history:
                    instance.change_history = {"changes": []}
                elif "changes" not in instance.change_history:
                    instance.change_history["changes"] = []

                instance.change_history["changes"].append(change_history_entry)
                instance.save(update_fields=["change_history"])

        return super().update(instance, validated_data)

    def to_representation(self, instance):

        from src.serializers.client_serializer import ClientSimpleSerializer

        response = super().to_representation(instance)
        response["client"] = ClientSimpleSerializer(instance.client).data
        if instance.partner:
            response["partner"] = PartnerSimpleSerializer(instance.partner).data

        return response


class GetOrdersSerializer(serializers.ModelSerializer):

    service = ServiceSimpleSerializer()
    options = OptionSimpleSerializer(many=True)
    datetime_created = serializers.DateTimeField(
        format="%d.%m.%Y",
        read_only=True,
    )
    time_created = serializers.DateTimeField(
        source="datetime_created",
        format="%H:%M",
        read_only=True,
    )

    class Meta:
        model = Order
        fields: list[str] = [
            "id",
            "point_coordinates",
            "service",
            "options",
            "conditions",
            "address",
            "options_price",
            "delivery_price",
            "comment",
            "status",
            "datetime_created",
            "time_created",
            "technic_brand_model",
            "change_history",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        order_options = OrderOption.objects.filter(order=instance).select_related(
            "option"
        )
        representation["options"] = OrderOptionSerializer(
            order_options, many=True, context={"order": instance}
        ).data

        return representation


class GetClientOrdersSerializer(GetOrdersSerializer):

    partner = PartnerSimpleSerializer()

    class Meta(GetOrdersSerializer.Meta):
        fields: list[str] = GetOrdersSerializer.Meta.fields + ["partner", "conditions"]


class GetPartnerOrdersSerializer(serializers.ModelSerializer):

    client = serializers.SerializerMethodField()

    service = ServiceSimpleSerializer()
    options = OptionSimpleSerializer(many=True)
    datetime_created = serializers.DateTimeField(
        format="%d.%m.%Y",
        read_only=True,
    )
    time_created = serializers.DateTimeField(
        source="datetime_created",
        format="%H:%M",
        read_only=True,
    )

    def get_client(self, obj):
        from src.serializers.client_serializer import ClientSimpleSerializer

        serializer = ClientSimpleSerializer(obj.client)
        return serializer.data

    class Meta:
        model = Order
        fields: list[str] = [
            "id",
            "point_coordinates",
            "service",
            "options",
            "conditions",
            "address",
            "options_price",
            "delivery_price",
            "comment",
            "status",
            "datetime_created",
            "time_created",
            "technic_brand_model",
            "client",
            "commission",
            "technic_category",
            "change_history",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        order_options = OrderOption.objects.filter(order=instance).select_related(
            "option"
        )
        representation["options"] = OrderOptionSerializer(
            order_options, many=True, context={"order": instance}
        ).data

        return representation


class OrderListSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer()
    partner = PartnerSimplePhoneAndPhotoSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "datetime_created",
            "service",
            "total_price",
            "commission",
            "partner",
            "status",
        ]


class ChangeOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.OrderStatuses.choices)
