from collections.abc import Iterable

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError
from core.exceptions.errors.business import ResourceNotFound
from core.services import Service
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.types import RevokedSessionResult


class RevokeUserSessionsService(UserResolverMixin, Service[list[RevokedSessionResult]]):
    """Revoke every outstanding session of a user.

    Resolves the user from an email, phone number, or username, then
    blacklists every refresh token issued to that user that has not
    already been revoked. Sessions whose ``jti`` appears in
    ``exclude_jtis`` are left untouched — useful for keeping the
    session that initiated the action (e.g. a password change) alive.
    """

    def execute(
        self,
        identifier: str,
        *,
        exclude_jtis: Iterable[str] | None = None,
    ) -> list[RevokedSessionResult]:
        user = self._resolve_user(identifier)

        if user is None:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        excluded = set(exclude_jtis or ())

        token_objs = list(
            OutstandingToken.objects.filter(user=user)
            .exclude(jti__in=excluded)
            .only("jti", "token", "created_at", "expires_at", "user__username")
        )

        if not token_objs:
            return []

        outstanding_token_ids = [t.id for t in token_objs]
        already_blacklisted_jtis = set(
            BlacklistedToken.objects.filter(
                token_id__in=outstanding_token_ids
            ).values_list("token__jti", flat=True)
        )

        revoked: list[RevokedSessionResult] = []
        now = timezone.now()

        for token_obj in token_objs:
            if token_obj.jti in already_blacklisted_jtis:
                continue

            blacklisted = RefreshToken(token=token_obj.token).blacklist()
            revoked.append(
                RevokedSessionResult(
                    jti=token_obj.jti,
                    username=token_obj.user.username,
                    created_at=token_obj.created_at,
                    expires_at=token_obj.expires_at,
                    revoked_at=blacklisted.blacklisted_at
                    if isinstance(blacklisted, BlacklistedToken)
                    else now,
                )
            )

        return revoked
