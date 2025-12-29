"""Views for Contact model"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from website_api.models import Contact
from website_api.serializers import ContactSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список контактов",
        description="""
        Получить список контактной информации.
        
        **Возвращает только активные контакты** (is_active=True).
        
        **Типы контактов:**
        - `phone` - номера телефонов
        - `email` - электронная почта
        - `telegram` - Telegram
        - `whatsapp` - WhatsApp
        - `vk` - ВКонтакте
        - `instagram` - Instagram
        - `facebook` - Facebook
        
        Результаты отсортированы по display_order.
        """,
        tags=["Статический контент"],
        parameters=[
            OpenApiParameter(
                name='contact_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Тип контакта',
                required=False,
                enum=['phone', 'email', 'telegram', 'whatsapp', 'vk', 'instagram', 'facebook'],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Детали контакта",
        description="Получить детальную информацию о контакте. **Возвращает 404 для неактивных контактов.**",
        tags=["Статический контент"],
    ),
)
class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для контактной информации.
    
    Возвращает только активные контакты (is_active=True).
    Неактивные контакты не отображаются и возвращают 404.
    
    Возвращает список активных контактов:
    - Телефоны
    - Email
    - Социальные сети
    - Мессенджеры
    """
    queryset = Contact.objects.filter(is_active=True)
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['contact_type']
    ordering_fields = ['display_order']
    ordering = ['display_order', 'id']

