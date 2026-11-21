"""Service layer for changing an authenticated user's password.

Exposes :class:`ChangePasswordService`, which verifies the current
password, validates the new one against the project's password
validators, persists the change atomically, and revokes every other
session of the user — keeping the session that initiated the change
intact (when its ``jti`` is supplied).

Re-authentication via the current password is required even though the
caller is already authenticated: it protects against an attacker who has
gained temporary access to an unlocked device. This service does not
consult one-time codes, so ``CodePurpose`` and block state are
irrelevant here — the caller is already authenticated.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.types import PasswordChangeResult, RevokedSessionResult


class ChangePasswordService(Service[PasswordChangeResult]):
    """Change the password of an authenticated user.

    Verifies the current password, validates the new one against the
    project's password validators, persists the change atomically, and
    revokes every other session of the user — keeping the session that
    initiated the change intact.

    Re-authentication via ``current_password`` is required even though
    the caller is already authenticated: it protects against an attacker
    who has gained temporary access to an unlocked device.
    """

    def execute(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
        current_jti: str | None = None,
    ) -> PasswordChangeResult:
        """Change ``user``'s password and revoke other sessions.

        Args:
            user (User): The authenticated user changing their password.
            current_password (str): The user's current password, used
                for re-authentication.
            new_password (str): The desired new password. Must satisfy
                the project's password validators and differ from
                ``current_password``.
            current_jti (str | None, optional): The ``jti`` of the
                session that initiated the change. When supplied, that
                session is preserved; when ``None``, every session is
                revoked. Defaults to ``None``.

        Returns:
            PasswordChangeResult: The username, the change timestamp,
            and the list of revoked sessions.

        Raises:
            ValidationError: If ``current_password`` or ``new_password``
                is empty, or ``new_password`` fails the project's
                password validators; if ``current_password`` does not match,
                or ``new_password`` equals ``current_password``.
        """
        self._ensure_current_password(user=user, current_password=current_password)
        self._validate_new_password(user=user, new_password=new_password)

        if current_password == new_password:
            raise ValidationError(
                InvalidFormat(_t("New password must differ from the current password."))
            )

        now = timezone.now()

        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=["password"])
            revoked = self._revoke_other_sessions(user=user, keep_jti=current_jti)

        return PasswordChangeResult(
            username=user.username,
            changed_at=now,
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

    def _validate_new_password(self, *, user: User, new_password: str) -> None:
        """Validate the new password against the project's validators.

        Delegates to Django's ``validate_password`` so the rules defined
        in ``AUTH_PASSWORD_VALIDATORS`` (length, common-password list,
        similarity to user attributes, etc.) apply uniformly.

        Args:
            user (User): The authenticated user, passed to validators
                that compare the password against user attributes.
            new_password (str): The desired new password.

        Raises:
            ValidationError: If ``new_password`` is empty or fails any
                configured validator.
        """
        if not new_password:
            raise ValidationError(InvalidFormat(expected_format=_t("a new password")))

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid password.")),
                detail={"field_errors": exc.messages},
            ) from exc

    def _revoke_other_sessions(
        self, *, user: User, keep_jti: str | None
    ) -> list[RevokedSessionResult]:
        """Revoke every session of ``user`` except ``keep_jti``.

        The current session is preserved so the caller is not logged
        out by their own password change. When ``keep_jti`` is
        ``None``, every session is revoked — a safe default for
        callers that cannot supply a ``jti``.

        Args:
            user (User): The authenticated user.
            keep_jti (str | None): The ``jti`` of the session to
                preserve. When ``None``, every session is revoked.

        Returns:
            list[RevokedSessionResult]: The sessions that were revoked.
        """
        service = RevokeUserSessionsService()

        return service(
            identifier=user.username,
            exclude_jtis={keep_jti} if keep_jti else None,
        )
