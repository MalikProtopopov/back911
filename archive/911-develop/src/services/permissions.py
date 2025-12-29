from rest_framework import permissions
from rest_framework.viewsets import ViewSet

from src.services.admin.access_policy import AdminAccessPolicy


class IsTechnicOwner(permissions.BasePermission):
    """Пермишн для техники"""

    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class BaseAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view: ViewSet) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False

        admin = getattr(user, "admin", None)
        if not admin:
            return False
        return AdminAccessPolicy.can_access_view(admin, view.action)
