"""Service layer for deactivating a user's account.

Verifies the current password, sets ``is_active=False``, and revokes
every existing session of the user — so any device holding an old
refresh token is logged out. The account row itself is retained (soft
deactivation), so it can be reactivated by an administrator later.

The service does not interact with contact records beyond revoking
sessions, so ``CodePurpose`` and block state are irrelevant here —
deactivation is a user-account operation, not a contact operation.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.types import AccountDeactivationResult, RevokedSessionResult


class DeactivateAccountService(Service[AccountDeactivationResult]):
    """Deactivate the authenticated user's account.

    Verifies the current password, sets ``is_active=False`` atomically,
    and revokes every existing session of the user. The account row is
    retained (soft deactivation) so it can be reactivated later; contact
    records are left intact.

    Re-authentication via ``current_password`` is required even though
    the caller is already authenticated: it protects against an
    attacker who has gained temporary access to an unlocked device.
    """

    def execute(
        self,
        *,
        user: User,
        current_password: str,
        reason: str | None = None,
    ) -> AccountDeactivationResult:
        """Deactivate ``user``'s account and revoke all sessions.

        Args:
            user (User): The authenticated user deactivating their
                account.
            current_password (str): The user's current password, used
                for re-authentication.
            reason (str | None, optional): Free-text reason for
                deactivation, for auditing. Defaults to ``None``.

        Returns:
            AccountDeactivationResult: The username, the deactivation
            timestamp, and the list of revoked sessions.

        Raises:
            ValidationError: If ``current_password`` is empty.
            BusinessError: If ``current_password`` does not match, or
                the account is already inactive.
        """
        self._ensure_current_password(user=user, current_password=current_password)

        if not user.is_active:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Account is already deactivated."))
            )

        now = timezone.now()

        with transaction.atomic():
            revoked = self._revoke_all_sessions(user=user)
            user.is_active = False
            user.save(update_fields=["is_active"])

        self._record_reason(user=user, reason=reason)

        return AccountDeactivationResult(
            username=user.username,
            deactivated_at=now,
            revoked_sessions=revoked,
        )

    def _ensure_current_password(self, *, user: User, current_password: str) -> None:
        """Verify the supplied current password against the stored hash.

        Args:
            user (User): The authenticated user.
            current_password (str): The password supplied for
                re-authentication.

        Raises:
            ValidationError: If ``current_password`` is empty.
            BusinessError: If ``current_password`` does not match the
                stored password.
        """
        if not current_password:
            raise ValidationError(
                InvalidFormat(expected_format=_t("the current password"))
            )

        if not user.check_password(current_password):
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Current password is incorrect."))
            )

    def _revoke_all_sessions(self, *, user: User) -> list[RevokedSessionResult]:
        """Revoke every session of ``user``.

        All sessions are revoked — including the current one — because
        the account is being deactivated and no session should remain
        usable.

        Args:
            user (User): The authenticated user.

        Returns:
            list[RevokedSessionResult]: The sessions that were revoked.
        """
        return RevokeUserSessionsService()(identifier=user.username)

    def _record_reason(self, *, user: User, reason: str | None) -> None:
        """Record the deactivation reason for auditing.

        TODO: persist ``reason`` to an ``AuditLog`` model (or a
        ``deactivation_reason`` field on ``User``). Currently a no-op
        so the service remains usable before the audit model exists.

        Args:
            user (User): The deactivated user.
            reason (str | None): The free-text reason, if supplied.
        """
        ...
