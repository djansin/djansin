"""List active sessions of the authenticated user.

Returns every outstanding refresh token issued to the authenticated
user that is still usable (neither revoked nor expired). Requires
authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.user_sessions import UserSessionsEnvelopeSerializer
from djansin.kasejyan.services.user_sessions import ListUserSessionsService


class ListUserSessionsView(APIView):
    """List active sessions of the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List the current user's active sessions",
        description=(
            "Returns every outstanding refresh token issued to the "
            "authenticated user that is still usable (neither revoked "
            "nor expired), newest first."
        ),
        responses={
            200: UserSessionsEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Return the authenticated user's active sessions.

        Args:
            request: The incoming HTTP request.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the list of
            active sessions, newest first.

        Raises:
            BusinessError: When the resolved user does not exist.
                Raised by the service layer.
        """
        sessions = ListUserSessionsService()(identifier=request.user.username)
        return self.build_response(
            message=_t("Active sessions retrieved successfully."),
            code="AUTH_SESSIONS_LISTED",
            data=[session.to_dict() for session in sessions],
            status=status.HTTP_200_OK,
        )
