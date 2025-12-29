from django.urls import path, include

from users.routers import auth_router

urlpatterns = [
    path("auth/", include(auth_router.urls)),
]
