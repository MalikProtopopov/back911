from rest_framework import routers

from users.views import LoginRegisterViewSet

auth_router = routers.SimpleRouter()
auth_router.register(r"", LoginRegisterViewSet)
