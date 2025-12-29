"""URL configuration for website_api"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from website_api.views import (
    CityViewSet,
    ServiceViewSet,
    CityServiceView,
    OptionViewSet,
    TechnicCategoryViewSet,
    AdvantageViewSet,
    MetricViewSet,
    ContactViewSet,
    AppLinkViewSet,
    SeoMetaViewSet,
    LeadViewSet,
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

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path(
        'cities/<slug:city_slug>/services/<slug:service_slug>/',
        CityServiceView.as_view(),
        name='city-service'
    ),
]
