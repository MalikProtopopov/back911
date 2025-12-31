"""
In-memory кэш для данных ценообразования.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class PricingCache:
    """
    In-memory кэш для данных ценообразования.
    
    Хранит:
    - Типы параметров
    - Значения параметров
    - Зоны доставки
    
    Автоматически обновляется при изменениях в админке.
    """
    
    def __init__(self, ttl_minutes: int = 60):
        self._cache: Dict[str, Any] = {}
        self._last_update: Dict[str, datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def _is_expired(self, key: str) -> bool:
        if key not in self._last_update:
            return True
        return datetime.now() - self._last_update[key] > self._ttl
    
    def get(self, key: str) -> Optional[Any]:
        if self._is_expired(key):
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._last_update[key] = datetime.now()
    
    def invalidate(self, key: str = None) -> None:
        """Очистить кэш (весь или конкретный ключ)"""
        if key:
            self._cache.pop(key, None)
            self._last_update.pop(key, None)
        else:
            self._cache.clear()
            self._last_update.clear()
    
    def get_parameter_types(self):
        """Получить все типы параметров"""
        key = 'parameter_types'
        cached = self.get(key)
        if cached:
            return cached
        
        from website_api.models import ParameterType
        data = list(ParameterType.objects.filter(
            is_active=True
        ).prefetch_related('values').order_by('sort_order', 'title'))
        self.set(key, data)
        return data
    
    def get_parameter_values(self, parameter_type_code: str):
        """Получить значения для типа параметра"""
        key = f'parameter_values_{parameter_type_code}'
        cached = self.get(key)
        if cached:
            return cached
        
        from website_api.models import ParameterValue
        data = list(ParameterValue.objects.filter(
            parameter_type__code=parameter_type_code,
            parameter_type__is_active=True,
            is_active=True
        ).order_by('sort_order'))
        self.set(key, data)
        return data
    
    def get_delivery_zones(self, city_id: int):
        """Получить зоны доставки для города"""
        key = f'delivery_zones_{city_id}'
        cached = self.get(key)
        if cached:
            return cached
        
        from website_api.models import DeliveryZone
        data = list(DeliveryZone.objects.filter(
            city_id=city_id,
            is_active=True
        ))
        self.set(key, data)
        return data


# Singleton
pricing_cache = PricingCache(ttl_minutes=60)

