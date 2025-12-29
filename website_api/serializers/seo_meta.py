"""Serializers for SeoMeta model"""
from rest_framework import serializers
from website_api.models import SeoMeta


class SeoMetaSerializer(serializers.ModelSerializer):
    """Serializer for SEO metadata"""
    city_slug = serializers.CharField(source='city.slug', read_only=True, allow_null=True)
    city_title = serializers.CharField(source='city.title', read_only=True, allow_null=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True, allow_null=True)
    service_title = serializers.CharField(source='service.title', read_only=True, allow_null=True)
    
    class Meta:
        model = SeoMeta
        fields = [
            'id',
            'page_type',
            'city_slug',
            'city_title',
            'service_slug',
            'service_title',
            'title',
            'meta_description',
            'meta_keywords',
            'h1_title',
            'full_slug',
            'og_title',
            'og_description',
            'og_image_url',
            'schema_json',
            'is_active',
            'created_at',
            'updated_at',
        ]


class SeoMetaPublicSerializer(serializers.ModelSerializer):
    """Public serializer for SEO metadata (for frontend)"""
    
    class Meta:
        model = SeoMeta
        fields = [
            'page_type',
            'title',
            'meta_description',
            'meta_keywords',
            'h1_title',
            'full_slug',
            'og_title',
            'og_description',
            'og_image_url',
            'schema_json',
        ]

