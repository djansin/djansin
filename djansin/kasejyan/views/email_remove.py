"""Remove an email address from the authenticated user's account.

Verifies the one-time code sent to the email being removed, ensures the
user retains at least one other login method, and detaches the email.
Requires authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.permissions import IsEmailOwner
from djansin.kasejyan.serializers.email_remove import (
    RemoveEmailSerializer,
    RequestRemoveEmailSerializer,
)
from djansin.kasejyan.services.email_remove import RemoveEmailService
from djansin.kasejyan.services.email_remove_request import RequestRemoveEmailService


class RemoveEmailView(APIView):
    """Remove an email address from the authenticated user's account.

    Verifies the one-time code sent to the email being removed, guards
    against removing the user's last remaining login method, and
    detaches the email. The email row itself is retained with
    ``user=None`` so the address can be re-attached later.
    """

    permission_classes = [IsAuthenticated, IsEmailOwner]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle an email-removal request.

        Args:
            request: The incoming HTTP request carrying the email and
                verification code payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the username,
            the removed email address, and the time of removal.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the email does not belong to the user,
                the code is invalid or expired, or the removal would
                leave the user with no login method. Raised by the
                service layer.
        """
        serializer = RemoveEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RemoveEmailService()(
            user=request.user,
            email=serializer.validated_data["email"],
            code=serializer.validated_data["code"],
        )

        return self.build_response(
            message=_t("Email removed successfully."),
            code="EMAIL_REMOVED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )


class RequestRemoveEmailView(APIView):
    """Request a verification code to remove an email from the user's account.

    Verifies ownership of the email, guards against removing the user's
    last remaining login method, and dispatches a one-time code to the
    email. The code is then supplied to :class:`RemoveEmailView` to
    complete the removal.
    """

    permission_classes = [IsAuthenticated, IsEmailOwner]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle an email-removal code request.

        Args:
            request: The incoming HTTP request carrying the email
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the destination
            email and the code's expiry.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the email does not belong to the user,
                the removal would leave the user with no login method,
                or a still-valid code is already outstanding. Raised by
                the service layer.
        """
        serializer = RequestRemoveEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RequestRemoveEmailService()(
            user=request.user,
            email=serializer.validated_data["email"],
        )

        return self.build_response(
            message=_t("Verification code sent."),
            code="EMAIL_REMOVAL_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
