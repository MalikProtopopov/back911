"""Views for Metric model"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import Metric
from website_api.serializers import MetricSerializer, MetricPublicSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список метрик",
        description="""
        Получить список бизнес-метрик платформы.
        
        **Фильтрация:**
        - `metric_type` - тип метрики (platform, partner, client)
        - `visible_only=true` - только метрики видимые на публичном сайте (is_visible_on_site=True)
        - `is_visible_on_site` - фильтр по видимости (true/false)
        
        **Примеры метрик:**
        - Количество городов присутствия
        - Количество партнеров
        - Средний рейтинг платформы
        - Количество завершенных заказов
        
        Результаты отсортированы по display_order.
        """,
        tags=["Статический контент"],
        parameters=[
            OpenApiParameter(
                name='metric_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Тип метрики',
                required=False,
                enum=['platform', 'partner', 'client'],
            ),
            OpenApiParameter(
                name='visible_only',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Только метрики видимые на сайте (is_visible_on_site=True)',
                required=False,
            ),
            OpenApiParameter(
                name='is_visible_on_site',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Фильтр по видимости на сайте',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали метрики",
        description="Получить детальную информацию о конкретной метрике",
        tags=["Статический контент"],
    ),
)
class MetricViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для метрик платформы.
    
    Возвращает бизнес-метрики для отображения на сайте:
    - Количество городов
    - Количество партнеров
    - Средний рейтинг
    - И другие
    """
    queryset = Metric.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['metric_type', 'is_visible_on_site']
    ordering_fields = ['display_order']
    ordering = ['display_order', 'metric_key']
    
    def get_serializer_class(self):
        # Return public serializer by default for website visitors
        if self.request.query_params.get('visible_only') == 'true':
            return MetricPublicSerializer
        return MetricSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by visibility if requested
        if self.request.query_params.get('visible_only') == 'true':
            queryset = queryset.filter(is_visible_on_site=True)
        
        return queryset

