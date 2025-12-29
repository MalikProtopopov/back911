"""Views for City model"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import City, Service
from website_api.serializers import (
    CityListSerializer,
    CityDetailSerializer,
    ServiceListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список городов",
        description="""
        Получить список всех городов присутствия.
        
        **Возвращает только активные города** (is_active=True).
        
        **Функции:**
        - Поиск по названию города (параметр `search`)
        - Сортировка по `display_order` или `title`
        - Пагинация результатов
        
        **Информация о городе:**
        - Название и slug
        - Координаты (широта, долгота)
        - Порядок отображения
        - Краткое описание (если есть)
        
        Результаты отсортированы по display_order, затем по названию.
        """,
        tags=["Города"],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию города',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детальная информация о городе",
        description="""
        Получить полную информацию о городе по slug.
        
        **Возвращает 404 для неактивных городов.**
        
        **Включает:**
        - Базовая информация (название, slug, координаты)
        - Контент для страницы города (если есть)
        - SEO метаданные (если настроены)
        
        **Пример slug:** `moskva`, `sankt-peterburg`, `ekaterinburg`
        """,
        tags=["Города"],
    ),
)
class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для городов присутствия.
    
    Возвращает только активные города (is_active=True).
    Неактивные города не отображаются и возвращают 404.
    
    list:
    Возвращает список активных городов с базовой информацией.
    Поддерживает поиск по названию.
    
    retrieve:
    Возвращает детальную информацию о городе, включая контент и статистику.
    """
    queryset = City.objects.filter(is_active=True).select_related('content')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['display_order', 'title']
    ordering = ['display_order', 'title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CityListSerializer
        return CityDetailSerializer
    
    @extend_schema(
        summary="Услуги в городе",
        description="""
        Получить список всех услуг доступных в конкретном городе.
        
        **Возвращает только активные услуги** (is_active=True).
        
        **Примеры услуг:**
        - Шиномонтаж
        - Эвакуатор
        - Техническая помощь на дороге
        - Заправка топливом
        - Вскрытие автомобиля
        
        Для каждой услуги возвращается базовая информация и краткое описание.
        """,
        tags=["Города"],
    )
    @action(detail=True, methods=['get'], url_path='services')
    def services(self, request, slug=None):
        """Получить услуги доступные в городе"""
        city = self.get_object()
        services = Service.objects.filter(is_active=True).prefetch_related('contents')
        serializer = ServiceListSerializer(services, many=True)
        return Response(serializer.data)

