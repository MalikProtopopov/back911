"""Serializers for Metric model"""
from rest_framework import serializers
from website_api.models import Metric


class MetricSerializer(serializers.ModelSerializer):
    """Serializer for metrics"""
    
    class Meta:
        model = Metric
        fields = [
            'id',
            'metric_key',
            'value',
            'display_label',
            'description',
            'metric_type',
            'is_visible_on_site',
            'icon_name',
            'display_order',
            'last_updated',
        ]


class MetricPublicSerializer(serializers.ModelSerializer):
    """Public serializer for metrics (visible on website)"""
    
    class Meta:
        model = Metric
        fields = [
            'metric_key',
            'value',
            'display_label',
            'description',
            'icon_name',
            'display_order',
        ]

