"""Serializers for Document model"""
from rest_framework import serializers
from website_api.models import Document


class DocumentListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка документов (краткая информация)"""
    
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'version',
            'updated_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о документе"""
    
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'full_description',
            'version',
            'meta_title',
            'meta_description',
            'meta_keywords',
            'h1_title',
            'created_at',
            'updated_at',
        ]

