"""Request a verification code to change the user's email address.

Verifies the new email is not already owned, then dispatches a
one-time code to it. First step of the two-step email-change flow;
the second step is handled by :class:`ChangeEmailView`. Requires
authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.email_change import (
    ChangeEmailSerializer,
    RequestChangeEmailSerializer,
)
from djansin.kasejyan.services.email_change import ChangeEmailService
from djansin.kasejyan.services.email_change_request import RequestChangeEmailService


class ChangeEmailView(APIView):
    """Change the authenticated user's email address."""

    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle an email-change confirmation.

        Args:
            request: The incoming HTTP request carrying the new email
                and verification code payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the old and new
            email addresses and the time of the change.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the code is invalid or expired, or the
                new email is already owned by another user. Raised by
                the service layer.
        """
        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ChangeEmailService()(
            user=request.user,
            new_email=serializer.validated_data["new_email"],
            code=serializer.validated_data["code"],
        )

        return self.build_response(
            message=_t("Email changed successfully."),
            code="EMAIL_CHANGED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )


class RequestChangeEmailView(APIView):
    """Request a verification code to change the user's email address."""

    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle an email-change code request.

        Args:
            request: The incoming HTTP request carrying the new email
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the destination
            email and the code's expiry.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the email is invalid, already linked to
                the user, already taken by another user, or still has a
                valid code. Raised by the service layer.
        """
        serializer = RequestChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RequestChangeEmailService()(
            user=request.user,
            new_email=serializer.validated_data["new_email"],
        )

        return self.build_response(
            message=_t("Verification code sent."),
            code="EMAIL_CHANGE_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
