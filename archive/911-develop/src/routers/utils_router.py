from rest_framework import routers

from src.views.util_views import UtilitiesViewSet

utils_router = routers.SimpleRouter()
utils_router.register(r"", UtilitiesViewSet)
