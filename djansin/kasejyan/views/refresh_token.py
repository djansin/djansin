"""Refresh an access token using a valid refresh token.

Accepts a previously issued refresh token, validates it, rotates it
(blacklisting the old one), and returns a fresh JWT token pair in the
standard envelope. Open to unauthenticated clients, since the refresh
token itself is the credential.

The endpoint does not interact with contact records, so ``CodePurpose``
and block state are irrelevant here — refresh is a pure JWT operation.
A blocked email or phone does not prevent refreshing an existing
session; only the refresh token's own validity matters.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import AllowAny
from core.views import APIView, Response
from djansin.kasejyan.serializers.authenticate import AuthTokenEnvelopeSerializer
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
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

    @extend_schema(
        summary="Refresh an access token",
        description=(
            "Accepts a previously issued refresh token, validates it, "
            "rotates it (blacklisting the old one), and returns a "
            "fresh JWT token pair. Open to unauthenticated clients, "
            "since the refresh token itself is the credential. "
            "Blocked emails or phones do not affect refresh — only the "
            "refresh token's own validity matters."
        ),
        request=RefreshTokenSerializer,
        responses={
            200: AuthTokenEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
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

        token = RefreshTokenService()(refresh_token=refresh_token)

        return self.build_response(
            message=_t("Token refreshed successfully."),
            code="AUTH_TOKEN_REFRESHED",
            data=token.to_dict(),
            status=status.HTTP_200_OK,
        )
