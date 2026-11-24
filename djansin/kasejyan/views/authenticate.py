"""Authenticate an existing user or register a new one.

Accepts password-based or verification-code-based credentials,
resolves or provisions the user, and returns a JWT token pair in
the standard envelope. Open to unauthenticated clients.

Verification codes are validated with ``purpose=CodePurpose.AUTHENTICATE``;
a code issued for any other operation (e.g. email change or password
reset) is rejected. Blocked contacts are rejected by the verification
service before any code check, so a temporarily blocked email or phone
cannot be used to sign in until the block expires.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import AllowAny
from core.views import APIView, Response
from djansin.kasejyan.serializers.authenticate import (
    AuthenticateSerializer,
    AuthTokenEnvelopeSerializer,
)
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.services.access_token import AccessTokenService
from djansin.kasejyan.services.authenticate import AuthenticateService


class AuthenticateView(APIView):
    """Authenticate an existing user or register a new one.

    Accepts password-based or verification-code-based credentials,
    resolves or provisions the user, and returns a JWT token pair in
    the standard envelope. Open to unauthenticated clients.

    Verification codes are validated with
    ``purpose=CodePurpose.AUTHENTICATE``; a code issued for any other
    operation (e.g. email change or password reset) is rejected.
    Blocked contacts are rejected by the verification service before
    any code check, so a temporarily blocked email or phone cannot be
    used to sign in until the block expires.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Sign in or sign up",
        description=(
            "Authenticates an existing user or registers a new one. "
            "Accepts either ``password`` (with optional "
            "``password_confirm``) or a six-digit ``code`` sent to the "
            "identifier — never both. On success, returns a JWT token "
            "pair and the public user representation."
        ),
        request=AuthenticateSerializer,
        responses={
            200: AuthTokenEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a sign-in / sign-up request.

        Validates the payload, resolves or provisions the user, issues
        a JWT token pair, and returns it in a standard envelope.

        Args:
            request: The incoming HTTP request carrying the credentials
                payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the token pair
            and serialized user data.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            DomainError: When both ``password`` and ``code`` are
                supplied, or authentication fails (wrong password,
                invalid/expired/wrong-purpose code, blocked contact,
                unknown identifier). Raised by the service layer.
            BusinessError: When a newly generated username collides at
                the database level while provisioning a user. Raised by
                the service layer.
        """
        serializer = AuthenticateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data.get("identifier")
        password = serializer.validated_data.get("password")
        code = serializer.validated_data.get("code")

        registered_user = AuthenticateService()(
            identifier=identifier, password=password, code=code
        )

        token = AccessTokenService()(registered_user=registered_user)

        return self.build_response(
            message=_t("Authentication successful."),
            code="AUTH_TOKEN_ISSUED",
            data=token.to_dict(),
            status=status.HTTP_200_OK,
        )
