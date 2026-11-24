"""Change the username of the authenticated user.

Validates the new username's format and uniqueness, then persists the
change atomically. Requires authentication.

The endpoint does not interact with contact records, so ``CodePurpose``
and block state are irrelevant here — username change is a pure user
attribute update. Existing sessions are left intact, since the username
is not embedded in issued JWTs.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.username_change import (
    ChangeUsernameSerializer,
    UsernameChangeEnvelopeSerializer,
)
from djansin.kasejyan.services.username_change import ChangeUsernameService


class ChangeUsernameView(APIView):
    """Change the username of the authenticated user.

    Validates the new username's format and uniqueness, then persists
    the change. Unlike a password change, existing sessions are left
    intact — the username is not embedded in issued JWTs, so they
    remain valid.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change the current user's username",
        description=(
            "Validates the new username's format and uniqueness, then "
            "persists the change atomically. Existing sessions are "
            "left intact — the username is not embedded in issued "
            "JWTs, so they remain valid."
        ),
        request=ChangeUsernameSerializer,
        responses={
            200: UsernameChangeEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle a username-change request.

        Args:
            request: The incoming HTTP request carrying the new
                username payload.
            *args: Positional arguments forwarded by the URL dispatcher.
            **kwargs: Keyword arguments forwarded by the URL dispatcher.

        Returns:
            An enveloped ``200 OK`` response containing the old and
            new usernames and the time of the change.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the new username equals the current one,
                is already taken, or has an invalid format. Raised by
                the service layer.
        """
        serializer = ChangeUsernameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ChangeUsernameService()(
            user=request.user,
            new_username=serializer.validated_data["new_username"],
        )

        return self.build_response(
            message=_t("Username changed successfully."),
            code="USERNAME_CHANGED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
