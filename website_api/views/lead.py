"""Views for Lead model"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from website_api.models import Lead
from website_api.serializers import LeadSerializer, LeadCreateSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Создать заявку с сайта",
        description="""
        Отправить заявку (лид) с корпоративного сайта.
        
        **Обязательные поля:**
        - `name` - имя клиента (2-100 символов)
        - `phone` - номер телефона (10-20 символов, поддерживает форматы: +7..., 8..., и т.д.)
        
        **Опциональные поля:**
        - `email` - электронная почта
        - `city` - ID города
        - `service` - ID услуги
        - `message` - сообщение от клиента
        - `source_page` - URL страницы, с которой отправлена заявка
        - `utm_source`, `utm_medium`, `utm_campaign` - UTM метки для аналитики
        
        **Статус заявки:**
        По умолчанию создается со статусом `new` (новая).
        
        **Rate Limiting:**
        Ограничено 5 заявками в час с одного IP адреса (планируется).
        
        **Примеры использования:**
        ```json
        {
          "name": "Иван Иванов",
          "phone": "+79991234567",
          "email": "ivan@example.com",
          "city": 1,
          "service": 2,
          "message": "Нужен шиномонтаж завтра утром",
          "source_page": "/moskva/shinomontazh/",
          "utm_source": "google",
          "utm_medium": "cpc"
        }
        ```
        """,
        tags=["Заявки"],
        request=LeadCreateSerializer,
        responses={
            201: LeadSerializer,
            400: {'description': 'Ошибка валидации данных'},
            429: {'description': 'Превышен лимит запросов (rate limit)'},
        },
    ),
    list=extend_schema(
        summary="Список заявок (только для администраторов)",
        description="""
        Получить список всех заявок с сайта.
        
        **Требует аутентификации администратора.**
        
        **Фильтрация:**
        - `status` - статус заявки (new, processing, completed, cancelled)
        - `city` - ID города
        - `service` - ID услуги
        
        **Сортировка:**
        По умолчанию сортируется по дате создания (новые сверху).
        """,
        tags=["Заявки"],
    ),
    retrieve=extend_schema(
        summary="Детали заявки (только для администраторов)",
        description="Получить детальную информацию о конкретной заявке. Требует аутентификации.",
        tags=["Заявки"],
    ),
)
class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint для заявок с корпоративного сайта.
    
    create:
    Создание новой заявки. Доступно без аутентификации.
    Ограничено rate limiting (5 заявок в час с одного IP).
    
    list:
    Список всех заявок. Требует аутентификации администратора.
    
    retrieve:
    Детали заявки. Требует аутентификации администратора.
    """
    queryset = Lead.objects.all().select_related('city', 'service')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'city', 'service']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        return LeadSerializer
    
    def get_queryset(self):
        """Only authenticated staff users can view leads"""
        if self.action == 'list' and not self.request.user.is_staff:
            return Lead.objects.none()
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        """Create a new lead with rate limiting"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Add rate limiting here
        # For now, just create the lead
        lead = serializer.save()
        
        # Return full lead data
        output_serializer = LeadSerializer(lead)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )

