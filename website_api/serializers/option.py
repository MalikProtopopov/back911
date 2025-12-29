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
    """Option serializer with price for specific city"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'service_id',
            'service_title',
            'service_slug',
            'is_active',
            'price',
        ]
    
    def get_price(self, obj):
        """Get price for the city from context"""
        city = self.context.get('city')
        technic_category = self.context.get('technic_category')
        
        if not city:
            return None
        
        price_query = obj.prices.filter(city=city)
        
        if technic_category:
            price_query = price_query.filter(technic_category=technic_category)
        
        price = price_query.first()
        if price:
            return {
                'amount': str(price.amount),
                'technic_category': price.technic_category.title if price.technic_category else None
            }
        return None

