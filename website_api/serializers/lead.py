"""Serializers for Lead model"""
import re
from rest_framework import serializers
from website_api.models import Lead


class LeadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating leads"""
    
    class Meta:
        model = Lead
        fields = [
            'name',
            'phone',
            'email',
            'city',
            'service',
            'message',
            'source_page',
            'utm_source',
            'utm_medium',
            'utm_campaign',
        ]
    
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', value)
        
        # Russian phone numbers should have 11 digits (with country code)
        # or 10 digits (without country code)
        if len(digits) < 10 or len(digits) > 12:
            raise serializers.ValidationError(
                "Номер телефона должен содержать от 10 до 12 цифр"
            )
        
        return value
    
    def validate_name(self, value):
        """Validate name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Имя должно содержать минимум 2 символа"
            )
        return value.strip()


class LeadSerializer(serializers.ModelSerializer):
    """Full serializer for leads (admin view)"""
    city_title = serializers.CharField(source='city.title', read_only=True, allow_null=True)
    service_title = serializers.CharField(source='service.title', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'city',
            'city_title',
            'service',
            'service_title',
            'message',
            'source_page',
            'utm_source',
            'utm_medium',
            'utm_campaign',
            'status',
            'status_display',
            'created_at',
            'processed_at',
        ]
        read_only_fields = ['status', 'created_at', 'processed_at']

