"""Serializers for Contact model"""
from rest_framework import serializers
from website_api.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for contacts"""
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'contact_type',
            'value',
            'label',
            'icon_name',
            'is_active',
            'display_order',
        ]

