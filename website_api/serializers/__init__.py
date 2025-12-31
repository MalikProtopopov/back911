"""Serializers for website_api"""
from .city import CityListSerializer, CityDetailSerializer, CityContentSerializer
from .service import ServiceListSerializer, ServiceDetailSerializer, ServiceContentSerializer
from .option import (
    OptionListSerializer, 
    OptionDetailSerializer, 
    OptionWithCityPriceSerializer,
    OptionPriceSerializer,
    TechnicCategorySerializer,
)
from .advantage import AdvantageSerializer
from .metric import MetricSerializer, MetricPublicSerializer
from .contact import ContactSerializer
from .app_link import AppLinkSerializer
from .seo_meta import SeoMetaSerializer, SeoMetaPublicSerializer
from .lead import LeadSerializer, LeadCreateSerializer
from .pricing import (
    ParameterTypeSerializer,
    ParameterTypeDetailSerializer,
    ParameterValueSerializer,
    DeliveryZoneSerializer,
    OptionParameterTypeSerializer,
    ParameterPriceSerializer,
    PriceChangeLogSerializer,
    PriceCalculationRequestSerializer,
    PriceCalculationResponseSerializer,
)
from .document import DocumentListSerializer, DocumentDetailSerializer

__all__ = [
    # City
    'CityListSerializer',
    'CityDetailSerializer',
    'CityContentSerializer',
    # Service
    'ServiceListSerializer',
    'ServiceDetailSerializer',
    'ServiceContentSerializer',
    # Option
    'OptionListSerializer',
    'OptionDetailSerializer',
    'OptionWithCityPriceSerializer',
    'OptionPriceSerializer',
    'TechnicCategorySerializer',
    # Advantage
    'AdvantageSerializer',
    # Metric
    'MetricSerializer',
    'MetricPublicSerializer',
    # Contact
    'ContactSerializer',
    # AppLink
    'AppLinkSerializer',
    # SeoMeta
    'SeoMetaSerializer',
    'SeoMetaPublicSerializer',
    # Lead
    'LeadSerializer',
    'LeadCreateSerializer',
    # Pricing
    'ParameterTypeSerializer',
    'ParameterTypeDetailSerializer',
    'ParameterValueSerializer',
    'DeliveryZoneSerializer',
    'OptionParameterTypeSerializer',
    'ParameterPriceSerializer',
    'PriceChangeLogSerializer',
    'PriceCalculationRequestSerializer',
    'PriceCalculationResponseSerializer',
    # Document
    'DocumentListSerializer',
    'DocumentDetailSerializer',
]
