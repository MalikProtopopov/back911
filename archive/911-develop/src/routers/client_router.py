from rest_framework import routers

from src.views.client_view import ClientViewSet

client_router = routers.SimpleRouter()
client_router.register(r"", ClientViewSet)
