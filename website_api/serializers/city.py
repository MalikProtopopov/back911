"""Serializers for City model"""
from rest_framework import serializers
from website_api.models import City, CityContent


class CityContentSerializer(serializers.ModelSerializer):
    """Serializer for city content"""
    
    class Meta:
        model = CityContent
        fields = [
            'meta_title',
            'meta_description',
            'h1_title',
            'short_description',
            'full_description',
            'advantages_html',
            'partner_count',
            'avg_rating',
            'review_count',
            'updated_at',
        ]


class CityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for city lists"""
    partner_count = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'title', 'slug', 'partner_count']
    
    def get_partner_count(self, obj):
        """Get partner count from cached content"""
        if hasattr(obj, 'content') and obj.content:
            return obj.content.partner_count
        return 0


class CityDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single city"""
    content = CityContentSerializer(read_only=True)
    services_count = serializers.SerializerMethodField()
    delivery_zones = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            'id',
            'title',
            'slug',
            'is_active',
            'display_order',
            'content',
            'services_count',
            'delivery_zones',
            'created_at',
            'updated_at',
        ]
    
    def get_services_count(self, obj):
        """Get count of services available in this city"""
        from website_api.models import Service
        return Service.objects.filter(is_active=True).count()
    
    def get_delivery_zones(self, obj):
        """Get delivery zones for this city"""
        zones = obj.delivery_zones.filter(is_active=True)
        return [
            {
                "id": zone.id,
                "zone_name": zone.zone_name,
                "location_status": zone.location_status,
                "delivery_price": str(zone.delivery_price)
            }
            for zone in zones
        ]

