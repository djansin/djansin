"""Log out the authenticated user.

Revokes either the current refresh token or every active session of
the authenticated user, depending on the payload. Requires
authentication.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.signout import SignoutSerializer
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.services.signout import SignoutService


class SignoutView(APIView):
    """Log out the authenticated user.

    By default, blacklists the refresh token supplied in the payload
    (log out this device only). When ``all_devices`` is true, blacklists
    every outstanding refresh token of the authenticated user instead.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a logout request.

        Args:
            request: The incoming HTTP request carrying the logout payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response. For a single-session logout
            the data contains the revoked session metadata; for an
            all-devices logout it contains the list of revoked sessions.

        Raises:
            ValidationError: When the payload is invalid.
        """
        serializer = SignoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["all_devices"]:
            service = RevokeUserSessionsService()
            revoked = service(identifier=request.user.username)
            return self.build_response(
                message=_t("Logged out from all devices."),
                code="ALL_SESSIONS_REVOKED",
                data=[session.to_dict() for session in revoked],
                status=status.HTTP_200_OK,
            )

        service = SignoutService()
        revoked = service(
            refresh_token=serializer.validated_data["refresh"],
            user=request.user,
        )
        return self.build_response(
            message=_t("Logged out successfully."),
            code="SESSION_REVOKED",
            data=[revoked.to_dict()],
            status=status.HTTP_200_OK,
        )
