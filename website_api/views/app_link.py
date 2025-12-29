"""Views for AppLink model"""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import AppLink
from website_api.serializers import AppLinkSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Ссылки на приложения",
        description="""
        Получить ссылки на мобильные приложения.
        
        **Возвращает только активные ссылки** (is_active=True).
        
        **Платформы:**
        - `ios` - App Store (iOS)
        - `android` - Google Play (Android)
        
        **Типы приложений:**
        - `client` - приложение для клиентов
        - `partner` - приложение для партнеров
        
        **Пример использования:**
        - `/api/website/app-links/?platform=ios&app_type=client` - ссылка на iOS приложение для клиентов
        """,
        tags=["Статический контент"],
        parameters=[
            OpenApiParameter(
                name='platform',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Платформа',
                required=False,
                enum=['ios', 'android'],
            ),
            OpenApiParameter(
                name='app_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Тип приложения',
                required=False,
                enum=['client', 'partner'],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали ссылки",
        description="Получить детальную информацию о ссылке на приложение. **Возвращает 404 для неактивных ссылок.**",
        tags=["Статический контент"],
    ),
)
class AppLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для ссылок на мобильные приложения.
    
    Возвращает только активные ссылки (is_active=True).
    Неактивные ссылки не отображаются и возвращают 404.
    
    Возвращает ссылки на приложения для:
    - iOS (App Store)
    - Android (Google Play)
    
    Для двух типов пользователей:
    - Клиенты
    - Партнеры
    """
    queryset = AppLink.objects.filter(is_active=True)
    serializer_class = AppLinkSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['platform', 'app_type']

