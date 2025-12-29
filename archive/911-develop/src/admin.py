from django.contrib import admin

from src.models import (
    Order,
    OptionPrice,
    Service,
    Option,
    WorkingZone,
    PartnerService,
    PartnerServiceOption,
    QuestionAnswer,
)
from src.models.administrator import Admin
from src.models.city import City
from src.models.client import Client
from src.models.mobile_app_version import MobileAppVersion
from src.models.order import OrderConditions
from src.models.partner import Partner
from src.models.review import Review
from src.models.technic import Technic, TechnicCategory

admin.site.register(
    [
        Admin,
        City,
        Client,
        Order,
        OrderConditions,
        Partner,
        OptionPrice,
        PartnerService,
        PartnerServiceOption,
        Review,
        Service,
        Option,
        QuestionAnswer,
        Technic,
        TechnicCategory,
        WorkingZone,
        MobileAppVersion,
    ]
)
