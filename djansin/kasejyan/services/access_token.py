"""Service for issuing JWT token pairs to authenticated users.

Exposes :class:`AccessTokenService`, which mints a fresh refresh token
(and, implicitly, its paired access token) for a user who has just
successfully authenticated. The service is deliberately thin: it
delegates token construction entirely to ``simplejwt`` and returns the
result wrapped in :class:`~djansin.kasejyan.types.IssueTokenResult`.
"""

from rest_framework_simplejwt.tokens import RefreshToken

from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import IssueTokenResult, RegisteredUser


class AccessTokenService(Service[IssueTokenResult]):
    """Issue a fresh JWT token pair for an authenticated user.

    Re-fetches the user from the database to ensure the token is bound
    to a persisted, current row — the ``RegisteredUser`` value object
    passed in may be stale (e.g. built before a password change or a
    session revocation).
    """

    def execute(self, registered_user: RegisteredUser) -> IssueTokenResult:
        """Mint a fresh JWT token pair for ``registered_user``.

        Args:
            registered_user (RegisteredUser): The value object describing
                the user who has just authenticated. Only its ``pk`` is
                used; the rest of the payload is discarded.

        Returns:
            IssueTokenResult: The re-fetched user and the newly minted
            refresh token. The paired access token is available via
            ``result.refresh.access_token``.

        Raises:
            User.DoesNotExist: If the user identified by
                ``registered_user.pk`` no longer exists. This should not
                happen in normal flow (the caller just authenticated the
                user) but can occur under a race with account deletion.
        """
        user = User.objects.get(pk=registered_user.pk)
        refresh = RefreshToken.for_user(user)
        return IssueTokenResult(user=user, refresh=refresh)
