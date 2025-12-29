from rest_framework import routers

from src.views.rules_view import RulesViewSet

rules_router = routers.SimpleRouter()
rules_router.register(r"", RulesViewSet)
