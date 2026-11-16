from django.utils import timezone
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
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
        if not jti:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session identifier is required."))
            )

        token_obj = self._resolve_token(jti=jti, user=user)
        self._ensure_revokable(token_obj)

        now = timezone.now()

        try:
            RefreshToken(token=token_obj.token).blacklist()
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session could not be revoked."))
            ) from exc

        return RevokedSessionResult(
            jti=token_obj.jti,
            username=token_obj.user.username,
            created_at=token_obj.created_at,
            expires_at=token_obj.expires_at,
            revoked_at=now,
        )

    def _resolve_token(self, *, jti: str, user: User) -> OutstandingToken:
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
        if BlacklistedToken.objects.filter(token_id=token_obj.id).exists():
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session has already been revoked."))
            )

        if token_obj.expires_at <= timezone.now():
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Session has already expired."))
            )
