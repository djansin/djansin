"""Service layer for revoking every session of a user.

Resolves the user from an email, phone number, or username, then
blacklists every refresh token issued to that user that has not already
been revoked. Sessions whose ``jti`` appears in ``exclude_jtis`` are
left untouched — useful for keeping the session that initiated the
action (e.g. a password change) alive.

The service does not interact with contact records, so ``CodePurpose``
and block state are irrelevant here — revocation is a pure JWT
operation.
"""

import logging
from collections.abc import Iterable

from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.exceptions import TokenError
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


logger = logging.getLogger(__name__)


class RevokeUserSessionsService(UserResolverMixin, Service[list[RevokedSessionResult]]):
    """Revoke every outstanding session of a user.

    Resolves the user from an email, phone number, or username, then
    blacklists every refresh token issued to that user that has not
    already been revoked. Sessions whose ``jti`` appears in
    ``exclude_jtis`` are left untouched — useful for keeping the
    session that initiated the action (e.g. a password change) alive.

    Tokens that cannot be blacklisted (e.g. corrupt, signed with a
    rotated key) are logged and skipped, so a single bad token does not
    prevent the remaining sessions from being revoked.
    """

    def execute(
        self,
        identifier: str,
        *,
        exclude_jtis: Iterable[str] | None = None,
    ) -> list[RevokedSessionResult]:
        """Revoke every session of the resolved user.

        Args:
            identifier (str): An email address, phone number, or
                username identifying the user.
            exclude_jtis (Iterable[str] | None, optional): The ``jti``
                values of sessions to preserve. When ``None``, every
                session is revoked. Defaults to ``None``.

        Returns:
            list[RevokedSessionResult]: The sessions that were revoked.
            Sessions already revoked before this call, and sessions in
            ``exclude_jtis``, are omitted.

        Raises:
            BusinessError: If no user matches ``identifier``.
        """
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

        for token_obj in token_objs:
            if token_obj.jti in already_blacklisted_jtis:
                continue

            try:
                blacklisted = RefreshToken(token=token_obj.token).blacklist()
            except TokenError:
                # A corrupt or rotation-invalidated token must not
                # prevent the remaining sessions from being revoked.
                # Log and continue.
                logger.warning(
                    "Could not blacklist session %s for user %s",
                    token_obj.jti,
                    token_obj.user.username,
                )
                continue

            blacklisted = (
                blacklisted
                if isinstance(blacklisted, BlacklistedToken)
                else blacklisted[0]
            )

            revoked.append(
                RevokedSessionResult(
                    jti=token_obj.jti,
                    username=token_obj.user.username,
                    created_at=token_obj.created_at,
                    expires_at=token_obj.expires_at,
                    revoked_at=blacklisted.blacklisted_at,
                )
            )

        return revoked
