from rest_framework import routers

from src.views.balance_view import BalanceViewSet

balance_router = routers.SimpleRouter()
balance_router.register(r"", BalanceViewSet)
