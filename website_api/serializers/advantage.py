"""Serializers for Advantage model"""
from rest_framework import serializers
from website_api.models import Advantage


class AdvantageSerializer(serializers.ModelSerializer):
    """Serializer for advantages"""
    target_audience_display = serializers.CharField(
        source='get_target_audience_display',
        read_only=True
    )
    
    class Meta:
        model = Advantage
        fields = [
            'id',
            'target_audience',
            'target_audience_display',
            'title',
            'description',
            'icon_name',
            'display_order',
            'is_active',
        ]

