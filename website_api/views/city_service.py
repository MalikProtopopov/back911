"""Views for City-Service combination"""
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from website_api.models import City, Service, Option, SeoMeta, ServiceContent
from website_api.serializers import (
    CityListSerializer,
    ServiceListSerializer,
    OptionWithCityPriceSerializer,
    ServiceContentSerializer,
    SeoMetaPublicSerializer,
)


class CityServiceView(APIView):
    """
    API endpoint для получения полной информации об услуге в конкретном городе.
    
    Это основной endpoint для страниц вида "/москва/шиномонтаж/".
    
    **Возвращает только активные города и услуги.**
    Неактивные объекты возвращают 404.
    
    Возвращает:
    - Информацию о городе
    - Информацию об услуге
    - Список опций с ценами для этого города
    - Контент (специфичный для города или общий)
    - SEO метаданные для страницы
    """
    
    @extend_schema(
        summary="Полная информация об услуге в городе",
        description="""
        Получить всю необходимую информацию для отображения страницы услуги в конкретном городе.
        
        **Возвращает 404 если:**
        - Город не найден или неактивен (is_active=False)
        - Услуга не найдена или неактивна (is_active=False)
        
        **Что возвращается:**
        
        1. **city** - информация о городе:
           - Название, slug, координаты
           
        2. **service** - информация об услуге:
           - Название, slug, описание, иконка
           
        3. **options** - опции с ценами для этого города:
           - Только активные опции (is_active=True)
           - Только опции с установленными ценами в данном городе
           - Каждая опция включает массив цен по категориям техники
           
        4. **content** - HTML контент для страницы:
           - Приоритет отдается контенту специфичному для города
           - Если специфичного нет, возвращается общий контент услуги
           
        5. **seo** - SEO метаданные:
           - Title, Description, Keywords
           - Open Graph теги
           - Schema.org разметка
           - Если не найдены, возвращается null
        
        **Примеры URL:**
        - `/api/website/cities/moskva/services/shinomontazh/` - шиномонтаж в Москве
        - `/api/website/cities/sankt-peterburg/services/evakuator/` - эвакуатор в СПб
        """,
        tags=["Город + Услуга"],
        parameters=[
            OpenApiParameter(
                name='city_slug',
                type=str,
                location=OpenApiParameter.PATH,
                description='Slug города (например: moskva, sankt-peterburg)',
                required=True,
            ),
            OpenApiParameter(
                name='service_slug',
                type=str,
                location=OpenApiParameter.PATH,
                description='Slug услуги (например: shinomontazh, evakuator)',
                required=True,
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'city': {
                        'type': 'object',
                        'description': 'Информация о городе'
                    },
                    'service': {
                        'type': 'object',
                        'description': 'Информация об услуге'
                    },
                    'options': {
                        'type': 'array',
                        'description': 'Массив опций с ценами для данного города'
                    },
                    'content': {
                        'type': 'object',
                        'nullable': True,
                        'description': 'HTML контент страницы (может быть null)'
                    },
                    'seo': {
                        'type': 'object',
                        'nullable': True,
                        'description': 'SEO метаданные (может быть null)'
                    },
                }
            },
            404: {
                'description': 'Город или услуга не найдены / неактивны'
            }
        }
    )
    def get(self, request, city_slug, service_slug):
        """Получить информацию об услуге в городе"""
        city = get_object_or_404(City, slug=city_slug, is_active=True)
        service = get_object_or_404(Service, slug=service_slug, is_active=True)
        
        # Get options available in this city
        options = Option.objects.filter(
            service=service,
            is_active=True,
        ).prefetch_related(
            'prices',
            'prices__city',
            'prices__technic_category',
        )
        
        # Filter options that have prices in this city
        options_with_prices = [
            opt for opt in options 
            if opt.prices.filter(city=city).exists()
        ]
        
        # Get SEO for city-service combination
        seo = SeoMeta.objects.filter(
            page_type='city_service',
            city=city,
            service=service,
            is_active=True,
        ).first()
        
        # Get content for city-service combination
        content = ServiceContent.objects.filter(
            service=service,
            city=city,
        ).first()
        
        # If no city-specific content, get general service content
        if not content:
            content = ServiceContent.objects.filter(
                service=service,
                city__isnull=True,
            ).first()
        
        # Serialize data
        data = {
            'city': CityListSerializer(city).data,
            'service': ServiceListSerializer(service).data,
            'options': OptionWithCityPriceSerializer(
                options_with_prices, 
                many=True,
                context={'city': city}
            ).data,
            'content': ServiceContentSerializer(content).data if content else None,
            'seo': SeoMetaPublicSerializer(seo).data if seo else None,
        }
        
        return Response(data)

