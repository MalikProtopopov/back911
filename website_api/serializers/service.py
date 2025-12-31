"""Serializers for Service model"""
from rest_framework import serializers
from website_api.models import Service, ServiceContent


class ServiceContentSerializer(serializers.ModelSerializer):
    """Serializer for service content"""
    city_slug = serializers.CharField(source='city.slug', read_only=True, allow_null=True)
    city_title = serializers.CharField(source='city.title', read_only=True, allow_null=True)
    
    class Meta:
        model = ServiceContent
        fields = [
            'meta_title',
            'meta_description',
            'h1_title',
            'short_description',
            'description',
            'how_it_works_html',
            'benefits_html',
            'icon_url',
            'cover_image_url',
            'city_slug',
            'city_title',
            'updated_at',
        ]


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for service lists"""
    icon_url = serializers.SerializerMethodField()
    options_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'icon_url', 'options_count']
    
    def get_icon_url(self, obj):
        """Get icon URL from general content"""
        content = obj.contents.filter(city__isnull=True).first()
        if content:
            return content.icon_url
        return f'/static/icons/{obj.slug}.svg'
    
    def get_options_count(self, obj):
        """Get count of options for this service"""
        return obj.options.filter(is_active=True).count()


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single service"""
    content = serializers.SerializerMethodField()
    options_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id',
            'title',
            'slug',
            'is_active',
            'display_order',
            'content',
            'options_count',
            'created_at',
        ]
    
    def get_content(self, obj):
        """Get general service content (without city)"""
        content = obj.contents.filter(city__isnull=True).first()
        if content:
            return ServiceContentSerializer(content).data
        return None
    
    def get_options_count(self, obj):
        """Get count of options for this service"""
        return obj.options.filter(is_active=True).count()

