"""Permission classes for session ownership.

Ensure that a user can only act on sessions (refresh tokens) that
belong to them. Intended for endpoints that operate on a specific
session identified by its ``jti`` in the URL path.

Two variants are provided:

* :class:`IsSessionOwner` — only the session's owner may proceed.
* :class:`IsSessionOwnerOrAdmin` — the owner or a staff user may proceed.

Both must be combined with an authentication permission (e.g.
``IsAuthenticated``) so that ``request.user`` is populated before
ownership is checked.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from core.permissions import Permission
from core.requests import Request
from core.views import APIView


class IsSessionOwner(Permission):
    """Allow access only if the targeted session belongs to the user.

    Expects the session identifier (``jti``) to be present in the view's
    URL keyword arguments (``view.kwargs["jti"]``). If ``jti`` is
    missing, access is allowed so that URL dispatch or the view can
    handle the missing identifier (typically with a ``404``). If
    ``jti`` is present but the session does not exist or belongs to
    another user, access is denied — deliberately not distinguishing
    the two cases to avoid leaking session existence across users.

    Attributes:
        message (str): Human-readable denial message, translated at
            import time via ``gettext_lazy``.
    """

    message = _t("You do not have permission to access this session.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request may proceed.

        Args:
            request (Request): The incoming DRF request. Must have
                ``user`` populated by an authentication permission.
            view (APIView): The view handling the request. Used to read
                the ``jti`` path parameter from ``view.kwargs``.

        Returns:
            bool: ``True`` if ``jti`` is missing (deferred to URL
            dispatch or the view) or the session belongs to the
            authenticated user; ``False`` otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        jti = view.kwargs.get("jti")
        if not jti:
            # No jti in the URL → nothing to own; let the view handle
            # the missing identifier (or return 404 via URL dispatch).
            return True

        return OutstandingToken.objects.filter(jti=jti, user=request.user).exists()


class IsSessionOwnerOrAdmin(Permission):
    """Allow access if the session belongs to the user or they are staff.

    Expects ``jti`` in the view's URL keyword arguments. Staff users may
    act on any session; regular users only on their own. If ``jti`` is
    missing, access is allowed so that URL dispatch or the view can
    handle the missing identifier. If ``jti`` is present but the session
    does not belong to the user (and the user is not staff), access is
    denied — deliberately not distinguishing "does not exist" from
    "belongs to another user" to avoid leaking session existence.

    Attributes:
        message (str): Human-readable denial message, translated at
            import time via ``gettext_lazy``.
    """

    message = _t("You do not have permission to access this session.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request may proceed.

        Args:
            request (Request): The incoming DRF request. Must have
                ``user`` populated by an authentication permission.
            view (APIView): The view handling the request. Used to read
                the ``jti`` path parameter from ``view.kwargs``.

        Returns:
            bool: ``True`` if the user is staff, or ``jti`` is missing
            (deferred to URL dispatch or the view), or the session
            belongs to the authenticated user; ``False`` otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        jti = view.kwargs.get("jti")
        if not jti:
            # No jti in the URL → nothing to own; let the view handle
            # the missing identifier (or return 404 via URL dispatch).
            return True

        return OutstandingToken.objects.filter(jti=jti, user=request.user).exists()
