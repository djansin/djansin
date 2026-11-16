"""Request a verification code to change the user's phone number.

Verifies the new phone is not already owned, then dispatches a
one-time code to it. First step of the two-step phone-change flow;
the second step is handled by :class:`ChangePhoneView`. Requires
authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.phone_change import (
    ChangePhoneSerializer,
    RequestChangePhoneSerializer,
)
from djansin.kasejyan.services.phone_change import ChangePhoneService
from djansin.kasejyan.services.phone_change_request import RequestChangePhoneService


class ChangePhoneView(APIView):
    """Change the authenticated user's phone number."""

    permission_classes = [IsAuthenticated]

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
            BusinessError: When the code is invalid or expired, or the
                new phone is already owned by another user. Raised by
                the service layer.
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
    """Request a verification code to change the user's phone number."""

    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a phone-change code request.

        Args:
            request: The incoming HTTP request carrying the new phone
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the destination
            phone and the code's expiry.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the phone is invalid, already linked to
                the user, already taken by another user, or still has a
                valid code. Raised by the service layer.
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
