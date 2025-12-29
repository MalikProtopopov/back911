"""Views for Service model"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import Service, Option
from website_api.serializers import (
    ServiceListSerializer,
    ServiceDetailSerializer,
    OptionListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список услуг",
        description="""
        Получить список всех доступных услуг.
        
        **Возвращает только активные услуги** (is_active=True).
        
        **Доступные услуги:**
        - 🚗 Эвакуатор
        - 🔧 Шиномонтаж
        - ⚡ Техническая помощь на дороге
        - ⛽ Заправка топливом
        - 🔑 Вскрытие автомобиля
        - 🔋 Прикурить автомобиль
        - 🚛 Грузоперевозки
        - 🧰 Замена масла
        
        **Функции:**
        - Поиск по названию услуги (параметр `search`)
        - Сортировка по `display_order` или `title`
        - Пагинация результатов
        
        Результаты отсортированы по display_order.
        """,
        tags=["Услуги"],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию услуги',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детальная информация об услуге",
        description="""
        Получить полную информацию об услуге по slug.
        
        **Возвращает 404 для неактивных услуг.**
        
        **Включает:**
        - Название и slug услуги
        - Краткое и полное описание
        - Иконка услуги
        - Список доступных опций (активные)
        - HTML контент для страницы услуги (если есть)
        - SEO метаданные (если настроены)
        
        **Пример slug:** `shinomontazh`, `evakuator`, `tehnicheskaya-pomoshch`
        """,
        tags=["Услуги"],
    ),
)
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для услуг.
    
    Возвращает только активные услуги (is_active=True).
    Неактивные услуги не отображаются и возвращают 404.
    
    list:
    Возвращает список активных услуг с базовой информацией.
    
    retrieve:
    Возвращает детальную информацию об услуге, включая описание и контент.
    """
    queryset = Service.objects.filter(is_active=True).prefetch_related('options', 'contents')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['display_order', 'title']
    ordering = ['display_order', 'title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceDetailSerializer
    
    @extend_schema(
        summary="Опции услуги",
        description="""
        Получить список опций для конкретной услуги.
        
        **Возвращает только активные опции** (is_active=True).
        
        **Примеры опций для шиномонтажа:**
        - Радиус колеса (R13, R14, R15, и т.д.)
        - Тип автомобиля (легковой, кроссовер, внедорожник)
        - Балансировка колес
        - Замена вентилей
        
        Для каждой опции возвращается название, описание и цены по городам.
        """,
        tags=["Услуги"],
    )
    @action(detail=True, methods=['get'], url_path='options')
    def options(self, request, slug=None):
        """Получить опции услуги"""
        service = self.get_object()
        options = Option.objects.filter(
            service=service,
            is_active=True
        ).prefetch_related('prices')
        serializer = OptionListSerializer(options, many=True)
        return Response(serializer.data)

