"""Views for Advantage model"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import Advantage
from website_api.serializers import AdvantageSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список преимуществ",
        description="""
        Получить список преимуществ платформы.
        
        **Возвращает только активные преимущества** (is_active=True).
        
        Поддерживает фильтрацию по целевой аудитории:
        - `client` - преимущества для клиентов
        - `partner` - преимущества для партнеров
        - `both` - общие преимущества для всех
        
        Результаты отсортированы по display_order.
        """,
        tags=["Статический контент"],
        parameters=[
            OpenApiParameter(
                name='target_audience',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Целевая аудитория: client, partner, both',
                required=False,
                enum=['client', 'partner', 'both'],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали преимущества",
        description="Получить детальную информацию о конкретном преимуществе. **Возвращает 404 для неактивных преимуществ.**",
        tags=["Статический контент"],
    ),
)
class AdvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для преимуществ платформы.
    
    Возвращает только активные преимущества (is_active=True).
    Неактивные преимущества не отображаются и возвращают 404.
    
    Поддерживает фильтрацию по целевой аудитории:
    - client - для клиентов
    - partner - для партнеров
    - both - для обоих
    """
    queryset = Advantage.objects.filter(is_active=True)
    serializer_class = AdvantageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['target_audience']
    ordering_fields = ['display_order']
    ordering = ['display_order', 'id']

