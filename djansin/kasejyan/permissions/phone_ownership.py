"""Permission classes for phone ownership.

Ensures that a user can only act on phone numbers that belong to them.
Intended for endpoints that receive the target phone number in the
request payload rather than in the URL path.
"""

from django.utils.translation import gettext_lazy as _t

from core.permissions import Permission
from core.requests import Request
from core.utils.user_identifier import is_valid_phone
from core.views import APIView
from djansin.kasejyan.models import Phone


class IsPhoneOwner(Permission):
    message = _t("You do not have permission to access this phone number.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        phone = request.data.get("phone")
        if not (phone and is_valid_phone(identifier=phone)):
            # No phone in the payload → let the serializer reject the
            # request with a clear validation error (400), rather than
            # masking it as a permission failure (403).
            return True

        return Phone.objects.filter(number=phone, user=request.user).exists()


class IsPhoneOwnerOrAdmin(Permission):
    """Allow access only if the phone belongs to the user or they are staff.

    Expects the target phone number to be present in the request
    payload under the ``phone`` key. Staff users may act on any phone;
    regular users only on phones attached to their account. If the
    phone is missing from the payload or does not belong to the user,
    access is denied — deliberately not distinguishing "does not exist"
    from "belongs to another user" to avoid leaking phone ownership.

    Must be combined with an authentication permission (e.g.
    ``IsAuthenticated``) so that ``request.user`` is populated.
    """

    message = _t("You do not have permission to access this phone number.")

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        phone = request.data.get("phone")
        if not (phone and is_valid_phone(identifier=phone)):
            # No phone in the payload → let the serializer reject the
            # request with a clear validation error (400), rather than
            # masking it as a permission failure (403).
            return True

        return Phone.objects.filter(number=phone, user=request.user).exists()
