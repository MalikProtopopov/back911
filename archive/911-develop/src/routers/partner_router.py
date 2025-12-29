from rest_framework import routers

from src.views.partner_view import PartnerViewSet

partner_router = routers.SimpleRouter()
partner_router.register(r"", PartnerViewSet)
