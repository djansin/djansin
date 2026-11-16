"""Permission classes for email ownership.

Ensures that a user can only remove email addresses that belong to
them. Intended for endpoints that receive the target email in the
request payload rather than in the URL path.
"""

from django.utils.translation import gettext_lazy as _t

from core.permissions import Permission
from core.requests import Request
from core.utils.user_identifier import is_valid_email
from core.views import APIView
from djansin.kasejyan.models import Email


class IsEmailOwner(Permission):
    message = _t("You do not have permission to access this email.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        email = request.data.get("email")
        if not (email and is_valid_email(identifier=email)):
            # No email in the payload → let the serializer reject the
            # request with a clear validation error (400), rather than
            # masking it as a permission failure (403).
            return True

        return Email.objects.filter(address=email, user=request.user).exists()


class IsEmailOwnerOrAdmin(Permission):
    """Allow access only if the email belongs to the user or they are staff.

    Expects the target email address to be present in the request
    payload under the ``email`` key. Staff users may act on any email;
    regular users only on emails attached to their account. If the
    email is missing from the payload or does not belong to the user,
    access is denied — deliberately not distinguishing "does not exist"
    from "belongs to another user" to avoid leaking email ownership.

    Must be combined with an authentication permission (e.g.
    ``IsAuthenticated``) so that ``request.user`` is populated.
    """

    message = _t("You do not have permission to access this email.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        email = request.data.get("email")
        if not (email and is_valid_email(identifier=email)):
            # No email in the payload → let the serializer reject the
            # request with a clear validation error (400), rather than
            # masking it as a permission failure (403).
            return True

        return Email.objects.filter(address=email, user=request.user).exists()
