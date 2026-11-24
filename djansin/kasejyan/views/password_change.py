"""Change the password of the authenticated user.

Verifies the current password, sets the new one, and revokes every
other session of the user — keeping the session that initiated the
change intact (when its refresh token is supplied). Requires
authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError
from core.exceptions.errors.business import BusinessRuleViolation
from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.password_change import (
    ChangePasswordSerializer,
    PasswordChangeEnvelopeSerializer,
)
from djansin.kasejyan.services.password_change import ChangePasswordService


class ChangePasswordView(APIView):
    """Change the password of the authenticated user.

    Verifies the current password, sets the new one, and revokes every
    other session of the user. When the client supplies its refresh
    token, the session it belongs to is preserved; otherwise every
    session — including the current one — is revoked, and the user
    must sign in again.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change the current user's password",
        description=(
            "Verifies the current password, sets the new one, and "
            "revokes every other session of the user. When "
            "``refresh_token`` is supplied, the session it belongs to "
            "is preserved; otherwise every session — including the "
            "current one — is revoked."
        ),
        request=ChangePasswordSerializer,
        responses={
            200: PasswordChangeEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a password-change request.

        Args:
            request: The incoming HTTP request carrying the password
                change payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the outcome of
            the change, including the list of revoked sessions.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the current password is wrong, the new
                password is invalid, the new password equals the
                current one, or the supplied refresh token is
                structurally invalid. Raised by the service layer or
                :meth:`_resolve_current_jti`.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_jti = self._resolve_current_jti(
            serializer.validated_data.get("refresh_token")
        )

        result = ChangePasswordService()(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
            current_jti=current_jti,
        )

        return self.build_response(
            message=_t("Password changed successfully."),
            code="PASSWORD_CHANGED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )

    def _resolve_current_jti(self, refresh_token: str | None) -> str | None:
        """Extract the ``jti`` of the session that issued this request.

        The ``jti`` of an access token does NOT match any
        ``OutstandingToken`` row (those track refresh tokens), so the
        client must supply its refresh token for the current session
        to be preserved. If it doesn't, ``None`` is returned and every
        session is revoked — a safe default.

        Args:
            refresh_token (str | None): The refresh token supplied by
                the client, if any.

        Returns:
            str | None: The ``jti`` of the current session, or ``None``.

        Raises:
            BusinessError: When the supplied refresh token is structurally
                invalid.
        """
        if not refresh_token:
            return None

        try:
            return RefreshToken(token=refresh_token)["jti"]
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Invalid refresh token supplied."))
            ) from exc
