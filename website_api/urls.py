"""URL configuration for website_api"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from website_api.views import (
    CityViewSet,
    ServiceViewSet,
    CityServiceView,
    CityServiceOptionsView,
    OptionViewSet,
    TechnicCategoryViewSet,
    AdvantageViewSet,
    MetricViewSet,
    ContactViewSet,
    AppLinkViewSet,
    SeoMetaViewSet,
    LeadViewSet,
    DocumentViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'options', OptionViewSet, basename='option')
router.register(r'technic-categories', TechnicCategoryViewSet, basename='technic-category')
router.register(r'advantages', AdvantageViewSet, basename='advantage')
router.register(r'metrics', MetricViewSet, basename='metric')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'app-links', AppLinkViewSet, basename='app-link')
router.register(r'seo-meta', SeoMetaViewSet, basename='seo-meta')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    # Custom endpoints (должны быть ДО router.urls, чтобы не перехватывались ViewSet'ами)
    path(
        'cities/<slug:city_slug>/services/<slug:service_slug>/options/',
        CityServiceOptionsView.as_view(),
        name='city-service-options'
    ),
    path(
        'cities/<slug:city_slug>/services/<slug:service_slug>/',
        CityServiceView.as_view(),
        name='city-service'
    ),
    
    # Router URLs (в конце, чтобы не перехватывать кастомные пути)
    path('', include(router.urls)),
]
