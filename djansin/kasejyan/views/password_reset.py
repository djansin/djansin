"""Views for the password-reset flow.

Exposes two endpoints:

* :class:`RequestPasswordResetView` — sends a verification code to the
  user's preferred contact channel (phone, then email). The response is
  success-shaped regardless of whether the user exists, has a contact
  channel, or is blocked, to prevent user enumeration and block-state
  probing.
* :class:`PasswordResetView` — verifies the code, sets the new
  password, and revokes every existing session.

Both are open to unauthenticated clients, since the user has forgotten
their password and cannot authenticate.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import AllowAny
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.password_reset import (
    PasswordResetEnvelopeSerializer,
    PasswordResetRequestEnvelopeSerializer,
    PasswordResetSerializer,
    RequestPasswordResetSerializer,
)
from djansin.kasejyan.services.password_reset import PasswordResetService
from djansin.kasejyan.services.password_reset_request import RequestPasswordResetService


class RequestPasswordResetView(APIView):
    """Request a verification code to reset a user's password.

    Resolves the user from the supplied identifier, picks the preferred
    contact channel (phone, then email), and dispatches a fresh
    verification code. When the user does not exist, has no contact
    channel, or the selected contact is blocked, a success-shaped
    response is returned instead — indistinguishable from the real
    success path, to prevent enumeration and block-state probing. Open
    to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request a password-reset code",
        description=(
            "Sends a six-digit verification code to the user's "
            "preferred contact channel (phone, then email). The "
            "response is success-shaped regardless of whether the "
            "user exists, has a contact channel, or is blocked, so "
            "the endpoint cannot be used to enumerate users or probe "
            "block state. Open to unauthenticated clients."
        ),
        request=RequestPasswordResetSerializer,
        responses={
            200: PasswordResetRequestEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
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
            When the user does not exist, has no contact channel, or
            the selected contact is blocked, the response is
            indistinguishable from the success case.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When a still-valid code is already
                outstanding for the resolved contact. Raised by the
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
    session. The code must have been issued with
    ``purpose=CodePurpose.RESET_PASSWORD``; a code issued for any other
    operation is rejected. Blocked contacts are rejected before the
    password is touched. Open to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Confirm a password reset",
        description=(
            "Verifies the six-digit code sent to the user's contact "
            "channel, validates the new password, and persists it. "
            "Every existing session is revoked, forcing a fresh "
            "sign-in with the new password. The code must have been "
            "issued with ``purpose=CodePurpose.RESET_PASSWORD``. Open "
            "to unauthenticated clients."
        ),
        request=PasswordResetSerializer,
        responses={
            200: PasswordResetEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
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
            DomainError: When the code is invalid, expired, issued for a
                different purpose, or the contact is blocked. Raised by
                :class:`VerifyContactService`.
            BusinessError: When the user does not exist or the new
                password violates the password policy. Raised by the
                service layer.
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
