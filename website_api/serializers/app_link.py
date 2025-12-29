"""Serializers for AppLink model"""
from rest_framework import serializers
from website_api.models import AppLink


class AppLinkSerializer(serializers.ModelSerializer):
    """Serializer for app store links"""
    platform_display = serializers.CharField(
        source='get_platform_display',
        read_only=True
    )
    app_type_display = serializers.CharField(
        source='get_app_type_display',
        read_only=True
    )
    
    class Meta:
        model = AppLink
        fields = [
            'id',
            'platform',
            'platform_display',
            'app_type',
            'app_type_display',
            'store_url',
            'qr_code_url',
            'version',
            'is_active',
        ]

