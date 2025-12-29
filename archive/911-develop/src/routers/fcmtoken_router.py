from rest_framework import routers

from src.views.fcmtoken_view import FCMTokenViewSet

fcmtoken_router = routers.SimpleRouter()
fcmtoken_router.register(r"", FCMTokenViewSet)
