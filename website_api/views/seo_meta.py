"""Views for SeoMeta model"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import SeoMeta
from website_api.serializers import SeoMetaSerializer, SeoMetaPublicSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список SEO метаданных",
        description="""
        Получить список SEO метаданных для различных страниц сайта.
        
        **Возвращает только активные SEO записи** (is_active=True).
        
        **Фильтрация:**
        - `page_type` - тип страницы (home, city, service, city_service, about, contacts)
        - `slug` - полный slug страницы (например: `/moskva/shinomontazh/`)
        
        **Типы страниц:**
        - `home` - главная страница (/)
        - `city` - страница города (/moskva/)
        - `service` - страница услуги (/shinomontazh/)
        - `city_service` - услуга в городе (/moskva/shinomontazh/)
        - `about` - о компании
        - `contacts` - контакты
        
        **Включает:**
        - Title, Description, Keywords для SEO
        - Open Graph теги для соцсетей
        - Schema.org разметка для поисковых систем
        """,
        tags=["SEO"],
        parameters=[
            OpenApiParameter(
                name='page_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Тип страницы',
                required=False,
                enum=['home', 'city', 'service', 'city_service', 'about', 'contacts'],
            ),
            OpenApiParameter(
                name='full_slug',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Полный slug страницы (например: /moskva/shinomontazh/)',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали SEO метаданных",
        description="Получить детальные SEO метаданные. **Возвращает 404 для неактивных записей.**",
        tags=["SEO"],
    ),
)
class SeoMetaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для SEO метаданных.
    
    Возвращает только активные SEO записи (is_active=True).
    Неактивные записи не отображаются и возвращают 404.
    
    Возвращает метаданные для страниц сайта:
    - Title, Description, Keywords
    - Open Graph теги
    - Schema.org разметка
    
    Поддерживает фильтрацию по типу страницы и slug.
    """
    queryset = SeoMeta.objects.filter(is_active=True).select_related('city', 'service')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['page_type']
    ordering = ['page_type', 'full_slug']
    
    def get_serializer_class(self):
        # Return public serializer for frontend
        if self.action == 'by_slug' or self.request.query_params.get('format') == 'public':
            return SeoMetaPublicSerializer
        return SeoMetaSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by full slug if provided
        slug = self.request.query_params.get('full_slug')
        if slug:
            queryset = queryset.filter(full_slug=slug)
        
        return queryset
    
    @extend_schema(
        summary="SEO метаданные по slug",
        description="""
        Получить SEO метаданные для конкретной страницы по её slug.
        
        **Обязательные параметры:**
        - `slug` - полный slug страницы
        
        **Автоматическая нормализация slug:**
        - Добавляет `/` в начале и конце если отсутствует
        - Пример: `moskva/shinomontazh` → `/moskva/shinomontazh/`
        
        **Примеры запросов:**
        - `/api/website/seo-meta/by-slug/?slug=/` - SEO главной страницы
        - `/api/website/seo-meta/by-slug/?slug=/moskva/` - SEO страницы Москвы
        - `/api/website/seo-meta/by-slug/?slug=/moskva/shinomontazh/` - SEO услуги в городе
        
        **Возвращает:**
        - 200 - SEO метаданные найдены
        - 400 - Параметр slug не указан
        - 404 - SEO метаданные не найдены или страница неактивна
        """,
        tags=["SEO"],
        parameters=[
            OpenApiParameter(
                name='slug',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Полный slug страницы (обязательный)',
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='by-slug')
    def by_slug(self, request):
        """Получить SEO метаданные по slug страницы"""
        slug = request.query_params.get('slug')
        
        if not slug:
            return Response(
                {'error': 'Параметр slug обязателен'},
                status=400
            )
        
        # Normalize slug
        if not slug.startswith('/'):
            slug = '/' + slug
        if not slug.endswith('/'):
            slug = slug + '/'
        
        seo = self.get_queryset().filter(full_slug=slug).first()
        
        if not seo:
            return Response(
                {'error': 'SEO метаданные не найдены'},
                status=404
            )
        
        serializer = SeoMetaPublicSerializer(seo)
        return Response(serializer.data)

