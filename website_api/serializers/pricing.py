"""Serializers for pricing system"""
from rest_framework import serializers
from website_api.models import (
    ParameterType, ParameterValue, DeliveryZone, 
    OptionParameterType, ParameterPrice, PriceChangeLog
)


class ParameterValueSerializer(serializers.ModelSerializer):
    """Serializer for parameter value"""
    
    class Meta:
        model = ParameterValue
        fields = ['id', 'value', 'display_name', 'sort_order']


class ParameterTypeSerializer(serializers.ModelSerializer):
    """Serializer for parameter type"""
    values_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ParameterType
        fields = ['id', 'code', 'title', 'description', 'values_count']
    
    def get_values_count(self, obj):
        return obj.values.filter(is_active=True).count()


class ParameterTypeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for parameter type with values"""
    values = ParameterValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = ParameterType
        fields = ['id', 'code', 'title', 'description', 'values']


class DeliveryZoneSerializer(serializers.ModelSerializer):
    """Serializer for delivery zone"""
    
    class Meta:
        model = DeliveryZone
        fields = ['id', 'zone_name', 'location_status', 'delivery_price']


class OptionParameterTypeSerializer(serializers.ModelSerializer):
    """Serializer for option-parameter type link"""
    code = serializers.CharField(source='parameter_type.code', read_only=True)
    title = serializers.CharField(source='parameter_type.title', read_only=True)
    
    class Meta:
        model = OptionParameterType
        fields = ['code', 'title', 'is_required']


class ParameterPriceSerializer(serializers.ModelSerializer):
    """Serializer for parameter price"""
    display_name = serializers.CharField(source='parameter_value.display_name', read_only=True)
    parameter_type_code = serializers.CharField(
        source='parameter_value.parameter_type.code', read_only=True
    )
    
    class Meta:
        model = ParameterPrice
        fields = ['id', 'parameter_type_code', 'display_name', 'price_modifier']


class PriceChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for price change log"""
    
    class Meta:
        model = PriceChangeLog
        fields = [
            'id', 'entity_type', 'entity_id', 'entity_description',
            'old_value', 'new_value', 'changed_at', 'changed_by', 'reason'
        ]


class PriceCalculationRequestSerializer(serializers.Serializer):
    """Serializer for price calculation request"""
    option_id = serializers.IntegerField(required=True)
    city_id = serializers.IntegerField(required=True)
    technic_category_id = serializers.IntegerField(required=False, allow_null=True)
    parameter_values = serializers.DictField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    delivery_zone_id = serializers.IntegerField(required=False, allow_null=True)


class PriceBreakdownItemSerializer(serializers.Serializer):
    """Serializer for price breakdown item"""
    type = serializers.CharField()
    label = serializers.CharField()
    amount = serializers.CharField()


class PriceCalculationResponseSerializer(serializers.Serializer):
    """Serializer for price calculation response"""
    base_price = serializers.CharField()
    parameters_price = serializers.CharField()
    delivery_price = serializers.CharField()
    total_price = serializers.CharField()
    breakdown = PriceBreakdownItemSerializer(many=True)

