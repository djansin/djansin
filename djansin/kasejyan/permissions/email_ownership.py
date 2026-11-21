"""Permission classes for email ownership.

Ensure that a user can only act on email addresses that belong to them.
Intended for endpoints that receive the target email in the request
payload (under the ``email`` key) rather than in the URL path.

Two variants are provided:

* :class:`IsEmailOwner` — only the email's owner may proceed.
* :class:`IsEmailOwnerOrAdmin` — the owner or a staff user may proceed.

Both must be combined with an authentication permission (e.g.
``IsAuthenticated``) so that ``request.user`` is populated before
ownership is checked.
"""

from django.utils.translation import gettext_lazy as _t

from core.permissions import Permission
from core.requests import Request
from core.utils.user_identifier import is_valid_email
from core.views import APIView
from djansin.kasejyan.models import Email


class IsEmailOwner(Permission):
    """Allow access only if the email belongs to the authenticated user.

    Expects the target email address to be present in the request
    payload under the ``email`` key. If the email is missing or
    syntactically invalid, access is allowed so that the serializer can
    reject the request with a clear ``400`` validation error rather than
    masking it as a ``403``. If the email is present but does not belong
    to the user, access is denied — deliberately not distinguishing
    "does not exist" from "belongs to another user" to avoid leaking
    email ownership.

    Attributes:
        message (str): Human-readable denial message, translated at
            import time via ``gettext_lazy``.
    """

    message = _t("You do not have permission to access this email.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request may proceed.

        Args:
            request (Request): The incoming DRF request. Must have
                ``user`` populated by an authentication permission.
            view (APIView): The view handling the request. Unused, but
                part of the DRF permission contract.

        Returns:
            bool: ``True`` if the email is missing/invalid (deferred to
            the serializer) or belongs to the authenticated user;
            ``False`` otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        email = request.data.get("email")
        if not (email and is_valid_email(identifier=email)):
            # No (valid) email in the payload → let the serializer
            # reject the request with a clear validation error (400),
            # rather than masking it as a permission failure (403).
            return True

        return Email.objects.filter(address=email, user=request.user).exists()


class IsEmailOwnerOrAdmin(Permission):
    """Allow access if the email belongs to the user or they are staff.

    Expects the target email address to be present in the request
    payload under the ``email`` key. Staff users may act on any email;
    regular users only on emails attached to their account. If the
    email is missing or syntactically invalid, access is allowed so
    that the serializer can reject the request with a clear ``400``
    validation error rather than masking it as a ``403``. If the email
    is present but does not belong to the user (and the user is not
    staff), access is denied — deliberately not distinguishing "does
    not exist" from "belongs to another user" to avoid leaking email
    ownership.

    Attributes:
        message (str): Human-readable denial message, translated at
            import time via ``gettext_lazy``.
    """

    message = _t("You do not have permission to access this email.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request may proceed.

        Args:
            request (Request): The incoming DRF request. Must have
                ``user`` populated by an authentication permission.
            view (APIView): The view handling the request. Unused, but
                part of the DRF permission contract.

        Returns:
            bool: ``True`` if the user is staff, or the email is
            missing/invalid (deferred to the serializer), or belongs to
            the authenticated user; ``False`` otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        email = request.data.get("email")
        if not (email and is_valid_email(identifier=email)):
            # No (valid) email in the payload → let the serializer
            # reject the request with a clear validation error (400),
            # rather than masking it as a permission failure (403).
            return True

        return Email.objects.filter(address=email, user=request.user).exists()
