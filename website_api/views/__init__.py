"""Views for website_api"""
from .city import CityViewSet
from .service import ServiceViewSet
from .city_service import CityServiceView
from .option import OptionViewSet, TechnicCategoryViewSet
from .advantage import AdvantageViewSet
from .metric import MetricViewSet
from .contact import ContactViewSet
from .app_link import AppLinkViewSet
from .seo_meta import SeoMetaViewSet
from .lead import LeadViewSet

__all__ = [
    'CityViewSet',
    'ServiceViewSet',
    'CityServiceView',
    'OptionViewSet',
    'TechnicCategoryViewSet',
    'AdvantageViewSet',
    'MetricViewSet',
    'ContactViewSet',
    'AppLinkViewSet',
    'SeoMetaViewSet',
    'LeadViewSet',
]
