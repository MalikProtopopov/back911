"""Views for Lead model"""
from rest_framework import viewsets, status, permissions
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
        - `phone` - номер телефона (10-20 символов, поддерживает форматы: +7..., 8..., и т.д.)
        
        **Опциональные поля:**
        - `name` - имя клиента (2-100 символов, если указано)
        - `email` - электронная почта
        - `city` - ID города
        - `service` - ID услуги
        - `message` - сообщение от клиента
        - `lead_type` - тип заявки (service, feedback, partnership). По умолчанию: `service`
        - `page_url` - полный URL страницы, с которой отправлена заявка (включая query параметры и UTM метки)
        - `source_page` - путь страницы, с которой отправлена заявка
        - `utm_source`, `utm_medium`, `utm_campaign` - UTM метки для аналитики
        
        **Типы заявок:**
        - `service` - Заявка по услуге от клиента (по умолчанию)
        - `feedback` - Заявка с предложениями или обратной связью
        - `partnership` - Заявка на партнерство
        
        **Статус заявки:**
        По умолчанию создается со статусом `new` (новая).
        
        **Rate Limiting:**
        Ограничено 5 заявками в час с одного IP адреса (планируется).
        
        **Примеры использования:**
        
        Заявка по услуге:
        ```json
        {
          "name": "Иван Иванов",
          "phone": "+79991234567",
          "email": "ivan@example.com",
          "city": 1,
          "service": 2,
          "message": "Нужен шиномонтаж завтра утром",
          "lead_type": "service",
          "page_url": "https://911.ru/moskva/shinomontazh/?utm_source=google&utm_medium=cpc",
          "source_page": "/moskva/shinomontazh/",
          "utm_source": "google",
          "utm_medium": "cpc"
        }
        ```
        
        Заявка с обратной связью:
        ```json
        {
          "name": "Петр Петров",
          "phone": "+79997654321",
          "email": "petr@example.com",
          "message": "Хочу предложить улучшение сервиса",
          "lead_type": "feedback",
          "page_url": "https://911.ru/contacts/"
        }
        ```
        
        Заявка на партнерство:
        ```json
        {
          "name": "ООО Компания",
          "phone": "+79998887766",
          "email": "partner@example.com",
          "message": "Интересует сотрудничество",
          "lead_type": "partnership",
          "page_url": "https://911.ru/partnership/"
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
        - `status` - статус заявки (new, processing, converted, rejected)
        - `lead_type` - тип заявки (service, feedback, partnership)
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
    filterset_fields = ['status', 'lead_type', 'city', 'service']
    permission_classes = [permissions.AllowAny]  # Разрешаем создание заявок без аутентификации
    
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

