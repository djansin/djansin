"""Service layer for confirming a password reset.

Verifies the one-time code sent to the user's contact channel, sets
the new password, and revokes every existing session of the user —
forcing a fresh sign-in with the new credentials.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import PasswordResetResult


class PasswordResetService(UserResolverMixin, Service[PasswordResetResult]):
    """Confirm a password reset with a verification code.

    Resolves the user from ``identifier``, verifies the supplied code
    through the existing :class:`VerifyContactService`, validates the
    new password, persists it atomically, and revokes every existing
    session — so any device holding an old refresh token is logged out.
    """

    def execute(
        self,
        *,
        identifier: str,
        code: str,
        new_password: str,
    ) -> PasswordResetResult:
        user = self._resolve_user(identifier)

        if user is None:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        self._verify_code(identifier=identifier, code=code)
        self._validate_new_password(user=user, new_password=new_password)

        now = timezone.now()

        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=["password"])
            RevokeUserSessionsService()(identifier=user.username)

        return PasswordResetResult(
            username=user.username,
            changed_at=now,
        )

    def _verify_code(self, *, identifier: str, code: str) -> None:
        try:
            VerifyContactService()(identifier=identifier, code=code)
        except BusinessError:
            # Re-raise as a domain error with a clearer, password-reset
            # specific message — without leaking whether the code was
            # wrong, expired, or missing.
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Invalid or expired verification code.")
                )
            ) from None

    def _validate_new_password(self, *, user: User, new_password: str) -> None:
        if not new_password:
            raise ValidationError(InvalidFormat(expected_format=_t("a new password")))

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise BusinessError(
                InvalidFormat(expected_format=_t("a valid password.")),
                detail=exc.messages,
            ) from exc
