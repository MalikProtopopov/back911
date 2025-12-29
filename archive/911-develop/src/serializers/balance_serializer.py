from decimal import Decimal

from rest_framework import serializers


class CommissionPaymentSerializer(serializers.Serializer):

    pay_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
    )


class CreateDepositAndCommissionSerializer(serializers.Serializer):

    deposit_minimum = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
    )
