"""Service layer for signing out a user via a refresh token.

Resolves the session identified by the supplied refresh token, verifies
that it belongs to the given user (when supplied), and blacklists it.
Unlike :class:`RevokeSessionService`, the caller supplies the refresh
token itself rather than its ``jti`` — useful when the token is the
only credential the client holds at sign-out time.

The service does not interact with contact records, so ``CodePurpose``
and block state are irrelevant here — sign-out is a pure JWT operation.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import RevokedSessionResult


class SignoutService(Service[RevokedSessionResult]):
    """Sign out a user by blacklisting their refresh token.

    Resolves the session identified by ``refresh_token``, optionally
    scopes it to ``user`` (when supplied), and blacklists it. Raises a
    domain error if the token is invalid, the session does not exist,
    is owned by another user, has already been revoked, or has expired.
    """

    def execute(
        self, refresh_token: str, user: User | None = None
    ) -> RevokedSessionResult:
        """Blacklist the session identified by ``refresh_token``.

        Args:
            refresh_token (str): The refresh token to revoke. Must be
                a syntactically valid JWT.
            user (User | None, optional): When supplied, the session
                must belong to this user. When ``None``, ownership is
                not checked — use only when the token itself is the
                sole credential. Defaults to ``None``.

        Returns:
            RevokedSessionResult: The revoked session's metadata,
            including its ``jti``, owner, creation and expiry
            timestamps, and the revocation timestamp.

        Raises:
            ValidationError: If ``refresh_token`` is empty.
            BusinessError: If the token is invalid, the session does
                not exist, is owned by another user, has already been
                revoked, has expired, or cannot be blacklisted.
        """
        if not refresh_token:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid refresh token."))
            )

        jti = self._extract_jti(refresh_token)
        token_obj = self._resolve_token(jti=jti, user=user)
        self._ensure_revokable(token_obj)

        try:
            blacklisted = RefreshToken(token=token_obj.token).blacklist()
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session could not be revoked."))
            ) from exc

        return RevokedSessionResult(
            jti=token_obj.jti,
            username=token_obj.user.username,
            created_at=token_obj.created_at,
            expires_at=token_obj.expires_at,
            revoked_at=blacklisted.blacklisted_at
            if isinstance(blacklisted, BlacklistedToken)
            else timezone.now(),
        )

    def _extract_jti(self, refresh_token: str) -> str:
        """Extract the ``jti`` claim from ``refresh_token``.

        Parsing the token (rather than comparing its raw string to the
        stored column) avoids timing side-channels and tolerates
        whitespace or encoding variations introduced by clients.

        Args:
            refresh_token (str): The refresh token supplied by the
                client.

        Returns:
            str: The token's ``jti`` claim.

        Raises:
            BusinessError: If the token is not a structurally valid
                JWT.
        """
        try:
            return RefreshToken(token=refresh_token)["jti"]
        except TokenError as exc:
            raise BusinessError(ResourceNotFound(resource=_t("Session"))) from exc

    def _resolve_token(self, *, jti: str, user: User | None) -> OutstandingToken:
        """Resolve the session record for ``jti``.

        When ``user`` is supplied, the lookup is scoped to that user —
        a session belonging to someone else is reported as not found,
        to avoid leaking session existence across users.

        Args:
            jti (str): The unique identifier of the session.
            user (User | None): When supplied, the session must belong
                to this user.

        Returns:
            OutstandingToken: The matching session record.

        Raises:
            BusinessError: If no session exists for ``jti`` (optionally
                owned by ``user``).
        """
        qs = OutstandingToken.objects.filter(jti=jti).select_related("user")
        if user is not None:
            qs = qs.filter(user=user)

        token_obj = qs.first()
        if token_obj is None:
            raise BusinessError(ResourceNotFound(resource=_t("Session")))
        return token_obj

    def _ensure_revokable(self, token_obj: OutstandingToken) -> None:
        """Reject sessions that are already revoked or expired.

        Args:
            token_obj (OutstandingToken): The session record.

        Raises:
            BusinessError: If the session has already been blacklisted
                or has expired.
        """
        if BlacklistedToken.objects.filter(token_id=token_obj.id).exists():
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session has already been revoked."))
            )

        if token_obj.expires_at <= timezone.now():
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session has already expired."))
            )
