from rest_framework.permissions import SAFE_METHODS

from .base import Permission


class IsAdminOrReadOnly(Permission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class AllowAny(Permission):
    def has_permission(self, request, view):
        return True


class IsAuthenticated(Permission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
