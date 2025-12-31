"""Views for Document model"""
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, extend_schema_view

from website_api.models import Document
from website_api.serializers import DocumentListSerializer, DocumentDetailSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список документов",
        description="""
        Получить список всех активных документов.
        
        **Возвращает только активные документы** (is_active=True).
        
        Для каждого документа возвращается:
        - `id` - идентификатор
        - `title` - название документа
        - `slug` - URL идентификатор
        - `short_description` - краткое описание (HTML)
        - `version` - версия документа
        - `updated_at` - дата последнего обновления
        
        Результаты отсортированы по дате обновления (новые первые).
        """,
        tags=["Документы"],
    ),
    retrieve=extend_schema(
        summary="Детали документа",
        description="""
        Получить детальную информацию о документе по его slug.
        
        **Возвращает 404 для неактивных документов.**
        
        Возвращает полную информацию о документе:
        - Основные данные (title, slug, version)
        - Полный текст документа (full_description) в HTML формате
        - Краткое описание (short_description) в HTML формате
        - SEO метаданные (meta_title, meta_description, meta_keywords, h1_title)
        - Даты создания и обновления
        """,
        tags=["Документы"],
    ),
)
class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для документов сайта.
    
    Возвращает только активные документы (is_active=True).
    Неактивные документы не отображаются и возвращают 404.
    
    Поиск по slug: GET /api/website/documents/{slug}/
    """
    queryset = Document.objects.filter(is_active=True)
    lookup_field = 'slug'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'created_at', 'title']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentListSerializer
    
    def get_object(self):
        """
        Получить документ по slug.
        Возвращает 404 если документ не найден или неактивен.
        """
        slug = self.kwargs.get('slug')
        try:
            document = Document.objects.get(slug=slug)
        except Document.DoesNotExist:
            raise NotFound(detail="Документ не найден")
        
        if not document.is_active:
            raise NotFound(detail="Документ не найден")
        
        return document

