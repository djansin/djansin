"""Permission classes for session ownership.

Ensures that a user can only act on sessions (refresh tokens) that
belong to them. Intended for endpoints that operate on a specific
session identified by its ``jti`` in the URL path.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from core.permissions import Permission
from core.requests import Request
from core.views import APIView


class IsSessionOwner(Permission):
    """Allow access only if the targeted session belongs to the user.

    Expects the session identifier (``jti``) to be present in the view's
    URL keyword arguments (``kwargs["jti"]``). If the session does not
    exist or belongs to another user, access is denied with a 404-style
    ``PermissionDenied`` — deliberately not distinguishing the two cases
    to avoid leaking session existence across users.

    Must be combined with an authentication permission (e.g.
    ``IsAuthenticated``) so that ``request.user`` is populated.
    """

    message = _t("You do not have permission to access this session.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        jti = view.kwargs.get("jti")
        if not jti:
            # No jti in the URL → nothing to own; let the view handle
            # the missing identifier (or return 404 via URL dispatch).
            return True

        return OutstandingToken.objects.filter(jti=jti, user=request.user).exists()


class IsSessionOwnerOrAdmin(Permission):
    """Allow access to the session's owner or to staff users.

    Expects ``jti`` in the view's URL kwargs. Staff users may act on
    any session; regular users only on their own.
    """

    message = _t("You do not have permission to access this session.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        jti = view.kwargs.get("jti")
        if not jti:
            return True  # let the view/service handle missing jti

        return OutstandingToken.objects.filter(jti=jti, user=request.user).exists()
