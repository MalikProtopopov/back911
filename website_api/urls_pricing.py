"""URL configuration for pricing API"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from website_api.views import (
    ParameterTypeViewSet,
    DeliveryZoneListView,
    PriceCalculateView,
)

# Create router for pricing
pricing_router = DefaultRouter()
pricing_router.register(r'parameter-types', ParameterTypeViewSet, basename='parameter-type')

urlpatterns = [
    # Custom endpoints
    path(
        'cities/<int:city_id>/delivery-zones/',
        DeliveryZoneListView.as_view(),
        name='delivery-zones'
    ),
    path(
        'calculate/',
        PriceCalculateView.as_view(),
        name='calculate-price'
    ),
    
    # Router URLs
    path('', include(pricing_router.urls)),
]

