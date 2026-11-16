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
    """

    def execute(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
        current_jti: str | None = None,
    ) -> PasswordChangeResult:
        self._ensure_current_password(user=user, current_password=current_password)
        self._validate_new_password(user=user, new_password=new_password)

        if current_password == new_password:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("New password must differ from the current password.")
                )
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
        if not current_password:
            raise ValidationError(
                InvalidFormat(expected_format=_t("the current password"))
            )

        if not user.check_password(current_password):
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Current password is incorrect."))
            )

    def _validate_new_password(self, *, user: User, new_password: str) -> None:
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
        service = RevokeUserSessionsService()

        return service(
            identifier=user.username,
            exclude_jtis={keep_jti} if keep_jti else None,
        )
