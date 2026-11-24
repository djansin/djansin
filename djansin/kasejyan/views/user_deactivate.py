"""Deactivate the authenticated user's account.

Verifies the current password, sets ``is_active=False``, and revokes
every existing session of the user — so any device holding an old
refresh token is logged out. The account row itself is retained (soft
deactivation), so it can be reactivated by an administrator later.
Requires authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.user_deactivate import (
    AccountDeactivationEnvelopeSerializer,
    DeactivateAccountSerializer,
)
from djansin.kasejyan.services.user_deactivate import DeactivateAccountService


class DeactivateAccountView(APIView):
    """Deactivate the authenticated user's account.

    Verifies the current password, sets ``is_active=False``, and revokes
    every existing session of the user. The account row itself is
    retained (soft deactivation), so it can be reactivated by an
    administrator later.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Deactivate the current user's account",
        description=(
            "Deactivates the authenticated user's account. Requires the "
            "current password for re-authentication. All sessions are "
            "revoked upon success. The account row is retained (soft "
            "deactivation) so it can be reactivated later."
        ),
        request=DeactivateAccountSerializer,
        responses={
            200: AccountDeactivationEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle an account-deactivation request.

        Args:
            request: The incoming HTTP request carrying the
                deactivation payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the username,
            the deactivation timestamp, and the list of revoked
            sessions.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the current password is wrong, or the
                account is already inactive. Raised by the service
                layer.
        """
        serializer = DeactivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = DeactivateAccountService()(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            reason=serializer.validated_data.get("reason"),
        )

        return self.build_response(
            message=_t("Account deactivated successfully."),
            code="ACCOUNT_DEACTIVATED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
