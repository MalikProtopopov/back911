"""Views for Pricing API"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import ParameterType, ParameterValue, DeliveryZone, City
from website_api.serializers import (
    ParameterTypeSerializer,
    ParameterValueSerializer,
    DeliveryZoneSerializer,
    PriceCalculationRequestSerializer,
    PriceCalculationResponseSerializer,
)
from website_api.services import PricingService
from website_api.cache import pricing_cache


@extend_schema_view(
    list=extend_schema(
        summary="Список типов параметров",
        description="""
        Получить список всех активных типов параметров.
        
        **Примеры типов параметров:**
        - tire_radius (Радиус шины)
        - oil_type (Тип масла)
        - fuel_type (Тип топлива)
        - boom_height (Высота автовышки)
        
        Типы параметров используются для динамического ценообразования опций.
        """,
        tags=["Ценообразование"],
    ),
    retrieve=extend_schema(
        summary="Детали типа параметра",
        description="Получить детальную информацию о типе параметра с его значениями",
        tags=["Ценообразование"],
    ),
)
class ParameterTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для типов параметров.
    
    Типы параметров определяют, какие дополнительные параметры влияют на цену опции
    (например, радиус шины, тип масла, тип топлива).
    """
    queryset = ParameterType.objects.filter(is_active=True).prefetch_related('values')
    serializer_class = ParameterTypeSerializer
    lookup_field = 'code'
    
    @extend_schema(
        summary="Значения типа параметра",
        description="""
        Получить все значения для конкретного типа параметра.
        
        **Пример:** GET /api/pricing/parameter-types/tire_radius/values/
        
        Вернёт все доступные радиусы шин (R13, R14, R15, ..., R22).
        """,
        tags=["Ценообразование"],
        responses={200: ParameterValueSerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='values')
    def values(self, request, code=None):
        """Получить значения для типа параметра"""
        parameter_type = self.get_object()
        values = parameter_type.values.filter(is_active=True).order_by('sort_order')
        serializer = ParameterValueSerializer(values, many=True)
        return Response({
            "count": len(serializer.data),
            "next": None,
            "previous": None,
            "results": serializer.data
        })


class DeliveryZoneListView(APIView):
    """
    API endpoint для зон доставки в городе.
    """
    
    @extend_schema(
        summary="Зоны доставки в городе",
        description="""
        Получить список зон доставки для конкретного города.
        
        **Зоны доставки:**
        - in_city — В городе (обычно бесплатно или дёшево)
        - out_city — За городом (дороже)
        
        Цена доставки добавляется к базовой цене опции.
        """,
        tags=["Ценообразование"],
        parameters=[
            OpenApiParameter(
                name='city_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID города',
                required=True,
            ),
        ],
        responses={200: DeliveryZoneSerializer(many=True)},
    )
    def get(self, request, city_id):
        """Получить зоны доставки для города"""
        city = get_object_or_404(City, id=city_id, is_active=True)
        
        # Используем кэш
        zones = pricing_cache.get_delivery_zones(city_id)
        if not zones:
            zones = list(DeliveryZone.objects.filter(
                city=city,
                is_active=True
            ))
        
        serializer = DeliveryZoneSerializer(zones, many=True)
        return Response({
            "count": len(serializer.data),
            "next": None,
            "previous": None,
            "results": serializer.data
        })


class PriceCalculateView(APIView):
    """
    API endpoint для расчёта цены.
    """
    
    @extend_schema(
        summary="Расчёт цены",
        description="""
        Рассчитать итоговую цену услуги с учётом всех параметров.
        
        **Формула расчёта:**
        ```
        total_price = base_price (из OptionPrice)
                    + sum(parameter_modifiers) (из ParameterPrice)
                    + delivery_price (из DeliveryZone)
        ```
        
        **Пример запроса:**
        ```json
        {
            "option_id": 1,
            "city_id": 1,
            "parameter_values": {
                "tire_radius": 7
            },
            "delivery_zone_id": 2
        }
        ```
        
        **Пример ответа:**
        ```json
        {
            "base_price": "200.00",
            "parameters_price": "500.00",
            "delivery_price": "1500.00",
            "total_price": "2200.00",
            "breakdown": [
                {"type": "base", "label": "Замена колеса", "amount": "200.00"},
                {"type": "parameter", "label": "R19", "amount": "500.00"},
                {"type": "delivery", "label": "За городом", "amount": "1500.00"}
            ]
        }
        ```
        """,
        tags=["Ценообразование"],
        request=PriceCalculationRequestSerializer,
        responses={200: PriceCalculationResponseSerializer},
    )
    def post(self, request):
        """Рассчитать цену"""
        serializer = PriceCalculationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = PricingService.calculate_price(
            option_id=serializer.validated_data['option_id'],
            city_id=serializer.validated_data['city_id'],
            technic_category_id=serializer.validated_data.get('technic_category_id'),
            parameter_values=serializer.validated_data.get('parameter_values', {}),
            delivery_zone_id=serializer.validated_data.get('delivery_zone_id'),
        )
        
        return Response(result)

