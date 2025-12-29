"""Serializers for Option and OptionPrice models"""
from rest_framework import serializers
from website_api.models import Option, OptionPrice, TechnicCategory


class TechnicCategorySerializer(serializers.ModelSerializer):
    """Serializer for technic category"""
    
    class Meta:
        model = TechnicCategory
        fields = ['id', 'title']


class OptionPriceSerializer(serializers.ModelSerializer):
    """Serializer for option price"""
    city_slug = serializers.CharField(source='city.slug', read_only=True)
    city_title = serializers.CharField(source='city.title', read_only=True)
    technic_category_title = serializers.CharField(
        source='technic_category.title', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = OptionPrice
        fields = [
            'id',
            'city_slug',
            'city_title',
            'technic_category_id',
            'technic_category_title',
            'amount',
        ]


class OptionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for option lists"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    
    class Meta:
        model = Option
        fields = ['id', 'title', 'service_id', 'service_title', 'service_slug', 'is_active']


class OptionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single option with prices"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    prices = OptionPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'service_id',
            'service_title',
            'service_slug',
            'is_active',
            'prices',
        ]


class OptionWithCityPriceSerializer(serializers.ModelSerializer):
    """Option serializer with prices for specific city (all prices for all technic categories)"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'service_id',
            'service_title',
            'service_slug',
            'is_active',
            'prices',
        ]
    
    def get_prices(self, obj):
        """Get prices for the city from context, optionally filtered by technic category"""
        city = self.context.get('city')
        technic_category = self.context.get('technic_category')
        
        if not city:
            return []
        
        # Get prices for this option in this city
        prices = obj.prices.filter(city=city).select_related('technic_category')
        
        # If technic category is specified in context, filter by it
        if technic_category:
            prices = prices.filter(technic_category=technic_category)
        
        result = []
        for price in prices:
            result.append({
                'amount': str(price.amount),
                'technic_category': price.technic_category.title if price.technic_category else None
            })
        
        return result

