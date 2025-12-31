"""
URL configuration for website_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def api_root(request):
    """Root endpoint with API information"""
    return JsonResponse({
        "name": "911 Corporate Website API",
        "version": "1.0.0",
        "description": "REST API для корпоративного сайта 911",
        "endpoints": {
            "api_base": "/api/website/",
            "api_pricing": "/api/pricing/",
            "documentation": {
                "swagger_ui": "/api/docs/",
                "redoc": "/api/redoc/",
                "openapi_schema": "/api/schema/",
            },
            "main_endpoints": {
                "cities": "/api/website/cities/",
                "services": "/api/website/services/",
                "options": "/api/website/options/",
                "advantages": "/api/website/advantages/",
                "metrics": "/api/website/metrics/",
                "contacts": "/api/website/contacts/",
                "app_links": "/api/website/app-links/",
                "seo_meta": "/api/website/seo-meta/",
                "leads": "/api/website/leads/",
            },
            "pricing_endpoints": {
                "parameter_types": "/api/pricing/parameter-types/",
                "delivery_zones": "/api/pricing/cities/{city_id}/delivery-zones/",
                "calculate": "/api/pricing/calculate/",
            },
        },
        "admin": "/admin/",
    })

urlpatterns = [
    # Root endpoint
    path("", api_root, name="api-root"),
    
    path("admin/", admin.site.urls),
    
    # CKEditor 5
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # API endpoints
    path("api/website/", include("website_api.urls")),
    path("api/pricing/", include("website_api.urls_pricing")),
    
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
