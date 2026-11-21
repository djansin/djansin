"""Service layer for confirming a password reset.

Verifies the one-time code sent to the user's contact channel, sets
the new password, and revokes every existing session of the user —
forcing a fresh sign-in with the new credentials.

The code must have been issued with ``purpose=CodePurpose.RESET_PASSWORD``;
a code issued for any other operation (e.g. email change) is rejected
by :class:`VerifyContactService` before the password is touched. Blocked
contacts are also rejected there, so a temporarily blocked email or phone
cannot be used to reset a password until the block expires.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import ResourceNotFound
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.models.mixins.verifiable import VerifiableMixin
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import PasswordResetResult


class PasswordResetService(UserResolverMixin, Service[PasswordResetResult]):
    """Confirm a password reset with a verification code.

    Resolves the user from ``identifier``, verifies the supplied code
    through :class:`VerifyContactService` with
    ``purpose=CodePurpose.RESET_PASSWORD``, validates the new password,
    persists it atomically, and revokes every existing session — so any
    device holding an old refresh token is logged out.

    A code issued for any other operation (e.g. email change) is
    rejected by the verification service before the password is
    touched. Blocked contacts are also rejected there, so a temporarily
    blocked email or phone cannot be used to reset a password until the
    block expires.
    """

    def execute(
        self,
        *,
        identifier: str,
        code: str,
        new_password: str,
    ) -> PasswordResetResult:
        """Confirm a password reset.

        Args:
            identifier (str): The email address, phone number, or
                username identifying the user.
            code (str): The six-digit verification code sent to the
                user's contact channel, issued with
                ``purpose=CodePurpose.RESET_PASSWORD``.
            new_password (str): The new password to set.

        Returns:
            PasswordResetResult: The username and the time of the
            change.

        Raises:
            BusinessError: If the user does not exist, the code is
                invalid or expired, is issued for a different purpose,
                or the new password violates the password policy.
            DomainError: Propagated from :class:`VerifyContactService`
                for any verification failure (missing contact, blocked
                contact, wrong purpose, expired code, exhausted
                attempts, mismatched value).
        """
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
        """Verify the reset-password code for ``identifier``.

        Delegates to :class:`VerifyContactService` with
        ``purpose=CodePurpose.RESET_PASSWORD``, so a code issued for a
        different operation cannot authorize the reset. All
        verification failures — wrong purpose, expired code, exhausted
        attempts, blocked contact, mismatched value — surface as a
        :class:`DomainError` from the verification service; that error
        is allowed to propagate unchanged, so the caller cannot
        distinguish the underlying cause.

        Args:
            identifier (str): The email address or phone number that
                received the code.
            code (str): The six-digit verification code to check.

        Raises:
            DomainError: If verification fails for any reason.
        """
        VerifyContactService()(
            identifier=identifier,
            code=code,
            purpose=VerifiableMixin.CodePurpose.RESET_PASSWORD,
        )

    def _validate_new_password(self, *, user: User, new_password: str) -> None:
        """Validate the new password against the project's policy.

        Args:
            user (User): The user whose password is being reset.
            new_password (str): The new password to validate.

        Raises:
            ValidationError: If ``new_password`` is empty.
            BusinessError: If the password fails Django's password
                validators.
        """
        if not new_password:
            raise ValidationError(InvalidFormat(expected_format=_t("a new password")))

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise BusinessError(
                InvalidFormat(expected_format=_t("a valid password.")),
                detail=exc.messages,
            ) from exc
