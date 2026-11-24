"""Views for the phone-change flow.

Exposes two endpoints:

* :class:`RequestChangePhoneView` — dispatches a verification code to
  the new phone. The request step does not disclose whether the phone
  exists, is already owned, or is blocked: a generic success-shaped
  response is returned in all cases.
* :class:`ChangePhoneView` — verifies the code and swaps the user's
  current phone for the new one.

Both require authentication; the caller must be signed in to change
their phone.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.phone_change import (
    ChangePhoneSerializer,
    PhoneChangeEnvelopeSerializer,
    PhoneChangeRequestEnvelopeSerializer,
    RequestChangePhoneSerializer,
)
from djansin.kasejyan.services.phone_change import ChangePhoneService
from djansin.kasejyan.services.phone_change_request import RequestChangePhoneService


class ChangePhoneView(APIView):
    """Change the authenticated user's phone number.

    Verifies the one-time code sent to the new phone, then swaps the
    user's current phone for the new one. A blocked phone is rejected
    explicitly (after the code is verified); a phone owned by another
    account is also rejected explicitly (after the code is verified).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Confirm a phone change",
        description=(
            "Verifies the six-digit code sent to the new phone and "
            "swaps the authenticated user's current phone for the new "
            "one. The new phone must not be owned by another account. "
            "A temporarily blocked phone is rejected explicitly "
            "(after the code is verified)."
        ),
        request=ChangePhoneSerializer,
        responses={
            200: PhoneChangeEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a phone-change confirmation.

        Args:
            request: The incoming HTTP request carrying the new phone
                and verification code payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the old and new
            phone numbers and the time of the change.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            DomainError: When the phone has no pending change, or the
                code is invalid/expired/issued for a different purpose.
                Raised by the service layer.
            BusinessError: When the phone is temporarily blocked or is
                already owned by another user. Raised by the service
                layer.
        """
        serializer = ChangePhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ChangePhoneService()(
            user=request.user,
            new_phone=serializer.validated_data["new_phone"],
            code=serializer.validated_data["code"],
        )

        return self.build_response(
            message=_t("Phone number changed successfully."),
            code="PHONE_CHANGED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )


class RequestChangePhoneView(APIView):
    """Request a verification code to change the user's phone number.

    Verifies that the new phone is syntactically valid, then dispatches
    a one-time code to it. Ownership and block state are not disclosed
    at this step: a generic success-shaped response is returned in all
    cases, so the endpoint cannot be used to enumerate phones or probe
    ownership/block state.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Request a phone-change code",
        description=(
            "Dispatches a six-digit verification code to the supplied "
            "phone number. The response is success-shaped regardless "
            "of whether the phone exists, is already owned, or is "
            "blocked, so the endpoint cannot be used to enumerate "
            "phones or probe ownership/block state."
        ),
        request=RequestChangePhoneSerializer,
        responses={
            200: PhoneChangeRequestEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a phone-change code request.

        Args:
            request: The incoming HTTP request carrying the new phone
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the destination
            phone and the code's expiry. When the phone is blocked, the
            response is indistinguishable from the success case.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When a still-valid code is already
                outstanding for this phone. Raised by the service layer.
        """
        serializer = RequestChangePhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RequestChangePhoneService()(
            user=request.user,
            new_phone=serializer.validated_data["new_phone"],
        )

        return self.build_response(
            message=_t("Verification code sent."),
            code="PHONE_CHANGE_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
