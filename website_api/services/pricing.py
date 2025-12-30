"""Pricing calculation service"""
from decimal import Decimal
from typing import Dict, Any, Optional, List

from website_api.models import (
    Option, City, OptionPrice, ParameterPrice, 
    ParameterValue, DeliveryZone
)


class PricingService:
    """Service for price calculations"""
    
    @staticmethod
    def calculate_price(
        option_id: int,
        city_id: int,
        technic_category_id: int = None,
        parameter_values: Dict[str, int] = None,
        delivery_zone_id: int = None
    ) -> Dict[str, Any]:
        """
        Расчет итоговой цены.
        
        Args:
            option_id: ID опции
            city_id: ID города
            technic_category_id: ID категории техники (опционально)
            parameter_values: словарь {код_типа_параметра: id_значения} (опционально)
            delivery_zone_id: ID зоны доставки (опционально)
        
        Returns:
            {
                "base_price": "200.00",
                "parameters_price": "500.00",
                "delivery_price": "1000.00",
                "total_price": "1700.00",
                "breakdown": [
                    {"type": "base", "label": "Замена колеса", "amount": "200.00"},
                    {"type": "parameter", "label": "Радиус R19", "amount": "500.00"},
                    {"type": "delivery", "label": "За городом", "amount": "1000.00"}
                ]
            }
        """
        try:
            option = Option.objects.get(id=option_id)
            city = City.objects.get(id=city_id)
        except (Option.DoesNotExist, City.DoesNotExist):
            return {
                "error": "Option or City not found",
                "base_price": "0.00",
                "parameters_price": "0.00",
                "delivery_price": "0.00",
                "total_price": "0.00",
                "breakdown": []
            }
        
        breakdown: List[Dict[str, str]] = []
        
        # 1. Базовая цена опции
        option_price_query = OptionPrice.objects.filter(option=option, city=city)
        if technic_category_id:
            option_price_query = option_price_query.filter(
                technic_category_id=technic_category_id
            )
        else:
            option_price_query = option_price_query.filter(technic_category__isnull=True)
        
        option_price = option_price_query.first()
        base_price = option_price.amount if option_price else Decimal('0')
        
        breakdown.append({
            "type": "base",
            "label": option.title,
            "amount": str(base_price)
        })
        
        # 2. Модификаторы параметров (если опция имеет параметры)
        parameters_price = Decimal('0')
        
        if option.has_parameters and parameter_values:
            for param_type_code, param_value_id in parameter_values.items():
                param_price_query = ParameterPrice.objects.filter(
                    option=option,
                    parameter_value_id=param_value_id,
                    city=city
                )
                if technic_category_id:
                    param_price_query = param_price_query.filter(
                        technic_category_id=technic_category_id
                    )
                else:
                    param_price_query = param_price_query.filter(
                        technic_category__isnull=True
                    )
                
                param_price = param_price_query.first()
                
                if param_price:
                    parameters_price += param_price.price_modifier
                    
                    try:
                        param_value = ParameterValue.objects.get(id=param_value_id)
                        breakdown.append({
                            "type": "parameter",
                            "label": param_value.display_name,
                            "amount": str(param_price.price_modifier)
                        })
                    except ParameterValue.DoesNotExist:
                        pass
        
        # 3. Цена доставки (если указана зона)
        delivery_price = Decimal('0')
        
        if delivery_zone_id:
            delivery_zone = DeliveryZone.objects.filter(
                id=delivery_zone_id,
                city=city,
                is_active=True
            ).first()
            
            if delivery_zone:
                delivery_price = delivery_zone.delivery_price
                breakdown.append({
                    "type": "delivery",
                    "label": delivery_zone.zone_name,
                    "amount": str(delivery_price)
                })
        
        # Итого
        total_price = base_price + parameters_price + delivery_price
        
        return {
            "base_price": str(base_price),
            "parameters_price": str(parameters_price),
            "delivery_price": str(delivery_price),
            "total_price": str(total_price),
            "breakdown": breakdown
        }

