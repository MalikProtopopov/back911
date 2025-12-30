"""Views for website_api"""
from .city import CityViewSet
from .service import ServiceViewSet
from .city_service import CityServiceView, CityServiceOptionsView
from .option import OptionViewSet, TechnicCategoryViewSet
from .advantage import AdvantageViewSet
from .metric import MetricViewSet
from .contact import ContactViewSet
from .app_link import AppLinkViewSet
from .seo_meta import SeoMetaViewSet
from .lead import LeadViewSet
from .pricing import ParameterTypeViewSet, DeliveryZoneListView, PriceCalculateView

__all__ = [
    'CityViewSet',
    'ServiceViewSet',
    'CityServiceView',
    'CityServiceOptionsView',
    'OptionViewSet',
    'TechnicCategoryViewSet',
    'AdvantageViewSet',
    'MetricViewSet',
    'ContactViewSet',
    'AppLinkViewSet',
    'SeoMetaViewSet',
    'LeadViewSet',
    'ParameterTypeViewSet',
    'DeliveryZoneListView',
    'PriceCalculateView',
]
