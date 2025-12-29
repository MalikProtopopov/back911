from rest_framework import routers

from src.views.admin_view import AdminViewSet

admin_router = routers.SimpleRouter()
admin_router.register(r"", AdminViewSet)
