"""Views for the password-reset flow.

Exposes two endpoints:

* :class:`RequestPasswordResetView` — sends a verification code to the
  user's preferred contact channel (phone, then email).
* :class:`PasswordResetView` — verifies the code, sets the new
  password, and revokes every existing session.

Both are open to unauthenticated clients, since the user has forgotten
their password and cannot authenticate.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.permissions.auth_based import AllowAny
from core.views import APIView, Response
from djansin.kasejyan.serializers.password_reset import (
    PasswordResetSerializer,
    RequestPasswordResetSerializer,
)
from djansin.kasejyan.services.password_reset import PasswordResetService
from djansin.kasejyan.services.password_reset_request import RequestPasswordResetService


class RequestPasswordResetView(APIView):
    """Request a verification code to reset a user's password.

    Resolves the user from the supplied identifier, picks the preferred
    contact channel (phone, then email), and dispatches a fresh
    verification code. Open to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a password-reset code request.

        Args:
            request: The incoming HTTP request carrying the identifier
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the dispatch
            channel, the destination identifier, and the code's expiry.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the user does not exist, has no contact
                channel, or still has a valid code. Raised by the
                service layer.
        """
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RequestPasswordResetService()(
            identifier=serializer.validated_data["identifier"]
        )

        return self.build_response(
            message=_t("Verification code sent."),
            code="PASSWORD_RESET_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )


class PasswordResetView(APIView):
    """Confirm a password reset with a verification code.

    Verifies the code sent to the user's contact channel, validates the
    new password, persists it atomically, and revokes every existing
    session. Open to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a password-reset confirmation.

        Args:
            request: The incoming HTTP request carrying the identifier,
                code, and new password payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the username and
            the time of the change.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the user does not exist, the code is
                invalid or expired, or the new password violates the
                password policy. Raised by the service layer.
        """
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = PasswordResetService()(
            identifier=serializer.validated_data["identifier"],
            code=serializer.validated_data["code"],
            new_password=serializer.validated_data["new_password"],
        )

        return self.build_response(
            message=_t("Password reset successfully."),
            code="PASSWORD_RESET",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
