"""Views for the email-change flow.

Exposes two endpoints:

* :class:`RequestChangeEmailView` — dispatches a verification code to
  the new email. The request step does not disclose whether the email
  exists, is already owned, or is blocked: a generic success-shaped
  response is returned in all cases.
* :class:`ChangeEmailView` — verifies the code and swaps the user's
  current email for the new one.

Both require authentication; the caller must be signed in to change
their email.
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
    """Change the authenticated user's email address.

    Verifies the one-time code sent to the new email, then swaps the
    user's current email for the new one. A blocked email is rejected
    explicitly (after the code is verified); an email owned by another
    account is also rejected explicitly (after the code is verified).
    """

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
            DomainError: When the email has no pending change, or the
                code is invalid/expired/issued for a different purpose.
                Raised by the service layer.
            BusinessError: When the email is temporarily blocked or is
                already owned by another user. Raised by the service
                layer.
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
    """Request a verification code to change the user's email address.

    Verifies that the new email is syntactically valid, then dispatches
    a one-time code to it. Ownership and block state are not disclosed
    at this step: a generic success-shaped response is returned in all
    cases, so the endpoint cannot be used to enumerate emails or probe
    ownership/block state.
    """

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
            email and the code's expiry. When the email is blocked, the
            response is indistinguishable from the success case.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When a still-valid code is already
                outstanding for this email. Raised by the service layer.
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
