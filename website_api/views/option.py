"""Views for Option model"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import Option, City, TechnicCategory
from website_api.serializers import (
    OptionListSerializer,
    OptionDetailSerializer,
    OptionWithCityPriceSerializer,
    TechnicCategorySerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список опций",
        description="""
        Получить список всех опций услуг.
        
        **Возвращает только активные опции** (is_active=True).
        
        **Фильтрация:**
        - По услуге (`service` - ID услуги)
        - По slug услуги (`service__slug` - например, `shinomontazh`)
        
        **Примеры опций:**
        - Радиус колеса для шиномонтажа (R13-R22)
        - Тип автомобиля (легковой, кроссовер, внедорожник)
        - Расстояние эвакуации (до 10 км, 10-50 км, и т.д.)
        - Тип техники для перевозки
        
        **Пример запроса:**
        - `/api/website/options/?service__slug=shinomontazh` - опции для шиномонтажа
        """,
        tags=["Опции услуг"],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию опции',
                required=False,
            ),
            OpenApiParameter(
                name='service',
                type=int,
                location=OpenApiParameter.QUERY,
                description='ID услуги для фильтрации опций',
                required=False,
            ),
            OpenApiParameter(
                name='service__slug',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Slug услуги для фильтрации опций',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детальная информация об опции",
        description="""
        Получить полную информацию об опции с ценами по всем городам.
        
        **Возвращает 404 для неактивных опций.**
        
        **Включает:**
        - Название опции
        - Описание
        - Связанная услуга
        - Цены по всем городам (где доступна)
        - Категории техники (если применимо)
        """,
        tags=["Опции услуг"],
    ),
)
class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для опций услуг.
    
    Возвращает только активные опции (is_active=True).
    Неактивные опции не отображаются и возвращают 404.
    
    list:
    Возвращает список активных опций.
    Поддерживает фильтрацию по услуге.
    
    retrieve:
    Возвращает детальную информацию об опции с ценами по городам.
    """
    queryset = Option.objects.filter(is_active=True).select_related('service')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'service__slug']
    search_fields = ['title']
    ordering_fields = ['title']
    ordering = ['title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OptionListSerializer
        return OptionDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'prices',
                'prices__city',
                'prices__technic_category',
            )
        return queryset
    
    @extend_schema(
        summary="Опции по городу",
        description="""
        Получить опции с ценами для конкретного города.
        
        **Обязательные параметры:**
        - `city` - slug города (например, `moskva`)
        
        **Опциональные параметры:**
        - `service` - slug услуги для фильтрации (например, `shinomontazh`)
        
        **Возвращает только активные опции с ценами в указанном городе.**
        
        **Примеры запросов:**
        - `/api/website/options/by-city/?city=moskva` - все опции в Москве
        - `/api/website/options/by-city/?city=moskva&service=shinomontazh` - опции шиномонтажа в Москве
        
        **Цены:**
        Для каждой опции возвращается массив цен по категориям техники (если применимо).
        Если опция имеет фиксированную цену, возвращается одна цена без категории.
        """,
        tags=["Опции услуг"],
        parameters=[
            OpenApiParameter(
                name='city',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Slug города (обязательный)',
                required=True,
            ),
            OpenApiParameter(
                name='service',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Slug услуги для фильтрации (опционально)',
                required=False,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='by-city')
    def by_city(self, request):
        """Получить опции с ценами для конкретного города"""
        city_slug = request.query_params.get('city')
        service_slug = request.query_params.get('service')
        
        if not city_slug:
            return Response(
                {'error': 'Параметр city обязателен'},
                status=400
            )
        
        city = get_object_or_404(City, slug=city_slug, is_active=True)
        
        queryset = self.get_queryset().filter(
            prices__city=city
        ).distinct().prefetch_related(
            'prices',
            'prices__city',
            'prices__technic_category',
        )
        
        if service_slug:
            queryset = queryset.filter(service__slug=service_slug)
        
        serializer = OptionWithCityPriceSerializer(
            queryset, 
            many=True,
            context={'city': city}
        )
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Список категорий техники",
        description="""
        Получить список категорий техники для различных услуг.
        
        **Фильтрация:**
        - По услуге (`service` - ID услуги)
        - По slug услуги (`service__slug`)
        
        **Примеры категорий:**
        - Легковой автомобиль
        - Кроссовер
        - Внедорожник
        - Легкий коммерческий транспорт
        - Мотоцикл
        
        Категории техники используются для дифференциации цен на опции в зависимости от типа автомобиля.
        """,
        tags=["Опции услуг"],
        parameters=[
            OpenApiParameter(
                name='service',
                type=int,
                location=OpenApiParameter.QUERY,
                description='ID услуги для фильтрации',
                required=False,
            ),
            OpenApiParameter(
                name='service__slug',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Slug услуги для фильтрации',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали категории техники",
        description="Получить детальную информацию о категории техники",
        tags=["Опции услуг"],
    ),
)
class TechnicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для категорий техники.
    
    Категории используются для дифференциации цен на опции
    в зависимости от типа автомобиля или техники.
    """
    queryset = TechnicCategory.objects.all().select_related('service')
    serializer_class = TechnicCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['service', 'service__slug']

