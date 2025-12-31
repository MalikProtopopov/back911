"""Serializers for Option and OptionPrice models"""
from rest_framework import serializers
from website_api.models import Option, OptionPrice, TechnicCategory, ParameterPrice


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
    has_parameters = serializers.BooleanField(read_only=True)
    parameter_types = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = [
            'id', 'title', 'description', 'service_id', 'service_title', 
            'service_slug', 'has_parameters', 'parameter_types', 'is_active'
        ]
    
    def get_parameter_types(self, obj):
        """Возвращает типы параметров, если они есть"""
        if not obj.has_parameters:
            return []
        
        return [
            {
                "code": link.parameter_type.code,
                "title": link.parameter_type.title,
                "is_required": link.is_required
            }
            for link in obj.parameter_types.filter(
                parameter_type__is_active=True
            ).select_related('parameter_type')
        ]


class OptionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single option with prices"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    has_parameters = serializers.BooleanField(read_only=True)
    parameter_types = serializers.SerializerMethodField()
    prices = OptionPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'description',
            'service_id',
            'service_title',
            'service_slug',
            'has_parameters',
            'parameter_types',
            'is_active',
            'prices',
        ]
    
    def get_parameter_types(self, obj):
        """Возвращает типы параметров с их значениями"""
        if not obj.has_parameters:
            return []
        
        result = []
        for link in obj.parameter_types.filter(
            parameter_type__is_active=True
        ).select_related('parameter_type'):
            param_type = link.parameter_type
            
            values = [
                {
                    "id": value.id,
                    "value": value.value,
                    "display_name": value.display_name
                }
                for value in param_type.values.filter(is_active=True).order_by('sort_order')
            ]
            
            result.append({
                "code": param_type.code,
                "title": param_type.title,
                "is_required": link.is_required,
                "values": values
            })
        
        return result


class OptionWithCityPriceSerializer(serializers.ModelSerializer):
    """Option serializer with prices for specific city (all prices for all technic categories)"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True)
    has_parameters = serializers.BooleanField(read_only=True)
    parameter_types = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()
    parameter_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = [
            'id',
            'title',
            'description',
            'service_id',
            'service_title',
            'service_slug',
            'has_parameters',
            'parameter_types',
            'prices',
            'parameter_prices',
            'is_active',
        ]
    
    def get_parameter_types(self, obj):
        """Возвращает типы параметров с их значениями и ценами для города"""
        if not obj.has_parameters:
            return []
        
        result = []
        city = self.context.get('city')
        
        for link in obj.parameter_types.filter(
            parameter_type__is_active=True
        ).select_related('parameter_type'):
            param_type = link.parameter_type
            
            # Получаем значения с ценами для этого города
            values = []
            for value in param_type.values.filter(is_active=True).order_by('sort_order'):
                price_modifier = "0.00"
                if city:
                    param_price = ParameterPrice.objects.filter(
                        option=obj,
                        parameter_value=value,
                        city=city
                    ).first()
                    if param_price:
                        price_modifier = str(param_price.price_modifier)
                
                values.append({
                    "id": value.id,
                    "value": value.value,
                    "display_name": value.display_name,
                    "price_modifier": price_modifier
                })
            
            result.append({
                "code": param_type.code,
                "title": param_type.title,
                "is_required": link.is_required,
                "values": values
            })
        
        return result
    
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
    
    def get_parameter_prices(self, obj):
        """Цены параметров (если есть), сгруппированные по типу параметра"""
        if not obj.has_parameters:
            return {}
        
        city = self.context.get('city')
        if not city:
            return {}
        
        # Группируем по типу параметра
        result = {}
        
        for param_price in obj.parameter_prices.filter(
            city=city
        ).select_related('parameter_value', 'parameter_value__parameter_type'):
            param_type_code = param_price.parameter_value.parameter_type.code
            
            if param_type_code not in result:
                result[param_type_code] = []
            
            result[param_type_code].append({
                "value_id": param_price.parameter_value.id,
                "display_name": param_price.parameter_value.display_name,
                "price_modifier": str(param_price.price_modifier)
            })
        
        return result
