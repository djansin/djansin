"""Refresh an access token using a valid refresh token.

Accepts a previously issued refresh token, validates it, rotates it
(blacklisting the old one), and returns a fresh JWT token pair in the
standard envelope. Open to unauthenticated clients, since the refresh
token itself is the credential.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.exceptions.categories import BusinessError
from core.exceptions.errors.business import BusinessRuleViolation
from core.permissions.auth_based import AllowAny
from core.views import APIView, Response
from djansin.kasejyan.serializers.refresh_token import RefreshTokenSerializer
from djansin.kasejyan.services.refresh_token import RefreshTokenService


class RefreshTokenView(APIView):
    """Refresh an access token using a valid refresh token.

    Accepts a previously issued refresh token, validates it, rotates it
    (blacklisting the old one), and returns a fresh JWT token pair in
    the standard envelope. Open to unauthenticated clients, since the
    refresh token itself is the credential.
    """

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a token-refresh request.

        Validates the payload, delegates token rotation to the service
        layer, and returns the freshly issued token pair in a standard
        envelope.

        Args:
            request: The incoming HTTP request carrying the refresh
                token payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the new token
            pair.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the refresh token is invalid, expired,
                already revoked, or belongs to an inactive/missing user.
                Raised by the service layer.
        """
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get("refresh_token")

        token_service = RefreshTokenService()
        token = token_service(refresh_token=refresh_token)

        return self.build_response(
            message=_t("Token refreshed successfully."),
            code="AUTH_TOKEN_REFRESHED",
            data=token.to_dict(),
            status=status.HTTP_200_OK,
        )
