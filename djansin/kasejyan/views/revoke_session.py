"""Revoke a single session of the authenticated user.

Blacklists the refresh token identified by its ``jti``, provided it
belongs to the authenticated user. Requires authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.permissions import IsSessionOwner
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.revoke_session import (
    RevokedSessionEnvelopeSerializer,
)
from djansin.kasejyan.services.revoke_session import RevokeSessionService


class RevokeSessionView(APIView):
    """Revoke a single session of the authenticated user.

    Blacklists the refresh token identified by ``jti``, provided it
    belongs to the authenticated user. Returns the revoked session
    metadata in the standard envelope.
    """

    permission_classes = [IsAuthenticated, IsSessionOwner]

    @extend_schema(
        summary="Revoke a single session",
        description=(
            "Blacklists the refresh token identified by ``jti``, "
            "provided it belongs to the authenticated user. Returns "
            "the revoked session metadata."
        ),
        parameters=[
            OpenApiParameter(
                name="jti",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique JWT ID of the session to revoke.",
            ),
        ],
        responses={
            200: RevokedSessionEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def delete(self, request: HttpRequest, jti: str, *args, **kwargs) -> Response:
        """Handle a single-session revoke request.

        Args:
            request: The incoming HTTP request.
            jti: The unique identifier of the session (refresh token)
                to revoke, captured from the URL path.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the revoked
            session metadata.

        Raises:
            ValidationError: When ``jti`` is empty. Raised by the
                service layer.
            BusinessError: When the session does not exist, belongs to
                another user, has already been revoked, has expired,
                or cannot be blacklisted. Raised by the service layer.
        """
        revoked = RevokeSessionService()(jti=jti, user=request.user)

        return self.build_response(
            message=_t("Session revoked successfully."),
            code="SESSION_REVOKED",
            data=revoked.to_dict(),
            status=status.HTTP_200_OK,
        )
