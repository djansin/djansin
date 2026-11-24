"""Service layer for revoking a single session (refresh token).

Resolves the session by its ``jti``, verifies that it belongs to the
given user, and blacklists it. Raises a domain error if the session is
missing, owned by someone else, already revoked, or expired.

The service does not interact with contact records, so ``CodePurpose``
and block state are irrelevant here — revocation is a pure JWT
operation.
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


class RevokeSessionService(Service[RevokedSessionResult]):
    """Revoke a single session (refresh token) belonging to a user.

    Resolves the session by its ``jti``, verifies that it belongs to the
    given user, and blacklists it. Raises a domain error if the session
    is missing, owned by someone else, already revoked, or expired.
    """

    def execute(self, *, jti: str, user: User) -> RevokedSessionResult:
        """Revoke the session identified by ``jti``.

        Args:
            jti (str): The unique identifier of the session (refresh
                token) to revoke.
            user (User): The authenticated user requesting the
                revocation. The session must belong to this user.

        Returns:
            RevokedSessionResult: The revoked session's metadata,
            including its ``jti``, owner, creation and expiry
            timestamps, and the revocation timestamp.

        Raises:
            ValidationError: If ``jti`` is empty.
            BusinessError: If the session does not exist, belongs to
                another user, has already been revoked, has expired,
                or cannot be blacklisted.
        """
        if not jti:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid session identifier."))
            )

        token_obj = self._resolve_token(jti=jti, user=user)
        self._ensure_revokable(token_obj)

        try:
            blacklisted = RefreshToken(token=token_obj.token).blacklist()
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session could not be revoked."))
            ) from exc

        blacklisted = (
            blacklisted if isinstance(blacklisted, BlacklistedToken) else blacklisted[0]
        )
        return RevokedSessionResult(
            jti=token_obj.jti,
            username=token_obj.user.username,
            created_at=token_obj.created_at,
            expires_at=token_obj.expires_at,
            revoked_at=blacklisted.blacklisted_at,
        )

    def _resolve_token(self, *, jti: str, user: User) -> OutstandingToken:
        """Resolve the session record for ``jti`` owned by ``user``.

        Deliberately does not distinguish "not found" from "belongs to
        another user", to avoid leaking session existence across users.

        Args:
            jti (str): The unique identifier of the session.
            user (User): The authenticated user requesting the
                revocation.

        Returns:
            OutstandingToken: The matching session record.

        Raises:
            BusinessError: If no session exists for ``jti`` owned by
                ``user``.
        """
        token_obj = (
            OutstandingToken.objects.filter(jti=jti, user=user)
            .select_related("user")
            .first()
        )
        if token_obj is None:
            # We intentionally do NOT distinguish "not found" from
            # "belongs to another user" to avoid leaking session
            # existence across users.
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
