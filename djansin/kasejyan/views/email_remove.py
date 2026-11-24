"""Views for the email-removal flow.

Exposes two endpoints:

* :class:`RequestRemoveEmailView` — dispatches a verification code to
  the email being removed. Ownership and block state are checked, but
  a blocked email is not rejected here: removal is a legitimate
  cleanup operation.
* :class:`RemoveEmailView` — verifies the code and detaches the email
  from the user, provided at least one other login method remains.

Both require authentication; the caller must own the email being
removed.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.permissions import IsEmailOwner
from djansin.kasejyan.serializers.email_remove import (
    EmailRemovalEnvelopeSerializer,
    EmailRemovalRequestEnvelopeSerializer,
    RemoveEmailSerializer,
    RequestRemoveEmailSerializer,
)
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.services.email_remove import RemoveEmailService
from djansin.kasejyan.services.email_remove_request import RequestRemoveEmailService


class RemoveEmailView(APIView):
    """Remove an email address from the authenticated user's account.

    Verifies the one-time code sent to the email being removed, guards
    against removing the user's last remaining login method, and
    detaches the email. The email row itself is retained with
    ``user=None`` so the address can be re-attached later. A blocked
    email can still be removed.
    """

    permission_classes = [IsAuthenticated, IsEmailOwner]

    @extend_schema(
        summary="Remove an email address",
        description=(
            "Verifies the six-digit code sent to the email being "
            "removed and detaches it from the authenticated user, "
            "provided at least one other login method remains. The "
            "email row is retained with ``user=None`` so it can be "
            "re-attached later. A blocked email can still be removed."
        ),
        request=RemoveEmailSerializer,
        responses={
            200: EmailRemovalEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            403: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
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
            DomainError: When the code is invalid, expired, or issued
                for a different purpose. Raised by the service layer.
            BusinessError: When the email does not belong to the user,
                or the removal would leave the user with no login
                method. Raised by the service layer.
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

    Verifies ownership of the email and dispatches a one-time code to
    it. Ownership is enforced by :class:`IsEmailOwner` and re-checked
    by the service. A blocked email is not rejected here: removal is a
    legitimate cleanup operation.
    """

    permission_classes = [IsAuthenticated, IsEmailOwner]

    @extend_schema(
        summary="Request an email-removal code",
        description=(
            "Dispatches a six-digit verification code to the email "
            "being removed. Ownership is enforced by "
            "``IsEmailOwner`` and re-checked by the service. A "
            "blocked email is **not** rejected here: removal is a "
            "legitimate cleanup operation."
        ),
        request=RequestRemoveEmailSerializer,
        responses={
            200: EmailRemovalRequestEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            403: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
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
