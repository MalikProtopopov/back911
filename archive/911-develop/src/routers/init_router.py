from rest_framework import routers

from src.views.init_view import InitViewSet

init_router = routers.SimpleRouter()
init_router.register(r"", InitViewSet)
