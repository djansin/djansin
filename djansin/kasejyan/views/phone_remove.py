"""Views for the phone-removal flow.

Exposes two endpoints:

* :class:`RequestRemovePhoneView` — dispatches a verification code to
  the phone being removed. Ownership and block state are checked, but
  a blocked phone is not rejected here: removal is a legitimate
  cleanup operation.
* :class:`RemovePhoneView` — verifies the code and detaches the phone
  from the user, provided at least one other login method remains.

Both require authentication; the caller must own the phone being
removed.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.permissions import IsPhoneOwner
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.phone_remove import (
    PhoneRemovalEnvelopeSerializer,
    PhoneRemovalRequestEnvelopeSerializer,
    RemovePhoneSerializer,
    RequestRemovePhoneSerializer,
)
from djansin.kasejyan.services.phone_remove import RemovePhoneService
from djansin.kasejyan.services.phone_remove_request import RequestRemovePhoneService


class RemovePhoneView(APIView):
    """Remove a phone number from the authenticated user's account.

    Verifies the one-time code sent to the phone being removed, guards
    against removing the user's last remaining login method, and
    detaches the phone. The phone row itself is retained with
    ``user=None`` so the number can be re-attached later. A blocked
    phone can still be removed.
    """

    permission_classes = [IsAuthenticated, IsPhoneOwner]

    @extend_schema(
        summary="Remove a phone number",
        description=(
            "Verifies the six-digit code sent to the phone being "
            "removed and detaches it from the authenticated user, "
            "provided at least one other login method remains. The "
            "phone row is retained with ``user=None`` so it can be "
            "re-attached later. A blocked phone can still be removed."
        ),
        request=RemovePhoneSerializer,
        responses={
            200: PhoneRemovalEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a phone-removal request.

        Args:
            request: The incoming HTTP request carrying the phone and
                verification code payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the username,
            the removed phone number, and the time of removal.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            DomainError: When the code is invalid, expired, or issued
                for a different purpose. Raised by the service layer.
            BusinessError: When the phone does not belong to the user,
                or the removal would leave the user with no login
                method. Raised by the service layer.
        """
        serializer = RemovePhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RemovePhoneService()(
            user=request.user,
            phone=serializer.validated_data["phone"],
            code=serializer.validated_data["code"],
        )

        return self.build_response(
            message=_t("Phone number removed successfully."),
            code="PHONE_REMOVED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )


class RequestRemovePhoneView(APIView):
    """Request a verification code to remove a phone from the user's account.

    Verifies ownership of the phone and dispatches a one-time code to
    it. Ownership is enforced by :class:`IsPhoneOwner` and re-checked
    by the service. A blocked phone is not rejected here: removal is a
    legitimate cleanup operation.
    """

    permission_classes = [IsAuthenticated, IsPhoneOwner]

    @extend_schema(
        summary="Request a phone-removal code",
        description=(
            "Dispatches a six-digit verification code to the phone "
            "being removed. Ownership is enforced by ``IsPhoneOwner`` "
            "and re-checked by the service. A blocked phone is **not** "
            "rejected here: removal is a legitimate cleanup operation."
        ),
        request=RequestRemovePhoneSerializer,
        responses={
            200: PhoneRemovalRequestEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a phone-removal code request.

        Args:
            request: The incoming HTTP request carrying the phone
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the destination
            phone and the code's expiry.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the phone does not belong to the user,
                or a still-valid code is already outstanding. Raised by
                the service layer.
        """
        serializer = RequestRemovePhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RequestRemovePhoneService()(
            user=request.user,
            phone=serializer.validated_data["phone"],
        )

        return self.build_response(
            message=_t("Verification code sent."),
            code="PHONE_REMOVAL_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
