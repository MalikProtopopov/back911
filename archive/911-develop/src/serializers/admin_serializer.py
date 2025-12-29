from datetime import datetime
from dateutil.relativedelta import relativedelta

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from src.models.administrator import Admin
from src.services.admin.admin_orm import AdminCreator, check_phone_for_change_by_admin


class CreateOrUpdateAdminSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
        allow_blank=True,
        required=False,
    )
    phone = serializers.CharField(
        max_length=20,
        allow_blank=True,
        required=False,
        source="current_user.phone",
    )
    user_login = serializers.CharField(
        max_length=100,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Admin.objects.all(),
                message="Пользователь с таким логином уже существует",
            )
        ],
    )
    password = serializers.CharField(
        max_length=50,
        required=True,
        write_only=True,
        source="current_user.password",
    )
    admin_status = serializers.CharField()

    class Meta:
        model = Admin
        fields = [
            "id",
            "first_name",
            "phone",
            "user_login",
            "password",
            "admin_status",
            "role",
        ]

    def create(self, validated_data):
        first_name = validated_data.get("first_name")
        current_user = validated_data.get("current_user")
        if current_user:
            phone = current_user.get("phone")
            password = current_user.get("password")
        else:
            phone = None
        user_login = validated_data.get("user_login")
        role = validated_data.get("role")
        return AdminCreator(
            first_name=first_name,
            phone=phone,
            user_login=user_login,
            password=password,
            role=role,
        ).create_admin_with_user()

    def update(self, instance: Admin, validated_data):
        current_user_data = validated_data.get("current_user")
        current_user = instance.current_user

        instance.user_login = validated_data.get("user_login", instance.user_login)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.admin_status = validated_data.get(
            "admin_status", instance.admin_status
        )
        instance.role = validated_data.get("role", instance.role)
        instance.save()

        if current_user_data:
            phone = current_user_data.get("phone")
            if phone:
                check_phone_for_change_by_admin(phone, current_user)

            current_user.phone = phone
            password = current_user_data.get("password")
            if password:
                current_user.set_password(password)
            current_user.save()

        return instance


class AdminListSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=20, source="current_user.phone")
    datetime_created = serializers.DateTimeField(source="current_user.datetime_created")

    class Meta:
        model = Admin
        fields = [
            "id",
            "first_name",
            "phone",
            "user_login",
            "datetime_created",
            "admin_status",
            "role",
        ]


class CalculateCommissionRequestSerializer(serializers.Serializer):
    PERIOD_CHOICES = [
        ("custom", "Произвольный период"),
        ("last_month", "За последний месяц"),
        ("last_3_months", "За последние 3 месяца"),
        ("last_year", "За последний год"),
    ]

    partner_id = serializers.IntegerField(required=False, allow_null=True)
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    period_type = serializers.ChoiceField(
        choices=PERIOD_CHOICES, default="custom", required=False
    )

    def validate(self, attrs):
        period_type = attrs.get("period_type", "custom")
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if period_type == "custom":
            if not date_from or not date_to:
                raise serializers.ValidationError(
                    "Для произвольного периода необходимо указать date_from и date_to"
                )
            if date_from > date_to:
                raise serializers.ValidationError(
                    "date_from не может быть больше date_to"
                )
        else:
            today = datetime.now().date()
            if period_type == "last_month":
                date_to = today
                date_from = today - relativedelta(months=1)
            elif period_type == "last_3_months":
                date_to = today
                date_from = today - relativedelta(months=3)
            elif period_type == "last_year":
                date_to = today
                date_from = today - relativedelta(years=1)

            attrs["date_from"] = date_from
            attrs["date_to"] = date_to

        return attrs


class OrderCommissionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    date = serializers.DateField()
    commission = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField()
    service_title = serializers.CharField(required=False, allow_null=True)
    total_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )


class CommissionResponseSerializer(serializers.Serializer):
    total_commission = serializers.DecimalField(max_digits=15, decimal_places=2)
    orders_count = serializers.IntegerField()
    period = serializers.DictField()
    orders = OrderCommissionSerializer(many=True, required=False)


class ServiceCommissionResponseSerializer(serializers.Serializer):
    total_commission = serializers.DecimalField(max_digits=15, decimal_places=2)
    orders_count = serializers.IntegerField()
    period = serializers.DictField()
