"""Purpose-scoped one-time verification codes for contact-like models.

Defines :class:`VerifiableMixin`, an abstract model mixin that adds
persisted state and behavior for issuing, expiring, validating, and
consuming one-time numeric verification codes. Each code is bound to a
:class:`CodePurpose` value, ensuring a code issued for one operation
cannot be replayed for another (e.g. a "change email" code cannot
authorize an "remove email" operation).

Purpose-specific helpers (``refresh_change_email_code``,
``refresh_remove_email_code``, …) wrap :meth:`refresh_code` so callers
cannot accidentally issue a code for the wrong purpose.

Module-level constants:
    MAX_ATTEMPTS (int): Maximum number of failed verification attempts
        allowed before a code is considered unusable.
    DEFAULT_CODE_TTL_MINUTES (int): Default time-to-live, in minutes, for
        a freshly issued verification code.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import ValidationError
from core.exceptions.errors.validation import InvalidValue
from core.models.mixins.abstract import AbstractModelMixin
from djansin.kasejyan.utils import generate_six_digit_code


MAX_ATTEMPTS = 3
DEFAULT_CODE_TTL_MINUTES = 1


class VerifiableMixin(AbstractModelMixin):
    """Abstract mixin adding purpose-scoped one-time verification codes.

    Provides persisted fields for tracking the verification lifecycle
    (verification timestamp, current code, code purpose, failed attempt
    count, and expiration timestamp) along with chainable helper methods
    to refresh, expire, increment, invalidate, and mark a code as
    verified.

    A code is only valid for the purpose it was issued for. Refreshing a
    code always overwrites both the code and its purpose, so a record
    never holds two concurrently valid codes.

    Subclasses are expected to be concrete Django models. This mixin does
    not declare a ``Meta`` other than ``abstract = True``.

    Attributes:
        verified_at (datetime.datetime | None): Timestamp when the contact
            was successfully verified, or ``None`` if not yet verified.
        verification_code (str): The current one-time code associated with
            this record. Maximum length is 6 characters.
        code_purpose (str): The operation this code authorizes. One of
            :class:`CodePurpose` values.
        code_use_attempts (int): Signed counter of verification attempts.
            Positive values represent failed attempts; a negative value
            marks a successful verification.
        code_expires_at (datetime.datetime | None): Timestamp at which the
            current code becomes invalid, or ``None`` when the code has
            been invalidated.
    """

    class CodePurpose(models.TextChoices):
        """The purpose a one-time verification code was issued for.

        A code issued for one purpose must not be accepted for another —
        e.g. a code requested to change an email must not authorize
        removing that email.

        Attributes:
            CHANGE_EMAIL: Authorizes replacing the user's email address.
            REMOVE_EMAIL: Authorizes detaching an email from the user.
            CHANGE_PHONE: Authorizes replacing the user's phone number.
            REMOVE_PHONE: Authorizes detaching a phone from the user.
            VERIFY_CONTACT: Authorizes initial ownership verification.
            RESET_PASSWORD: Authorizes resetting a forgotten password.
            AUTHENTICATE: Authorizes passwordless sign-in.
        """

        CHANGE_CONTACT = "chc", _t("Change email")
        REMOVE_CONTACT = "rmc", _t("Remove email")
        VERIFY_CONTACT = "vrc", _t("Verify contact")
        RESET_PASSWORD = "rsp", _t("Reset password")
        AUTHENTICATE = "ath", _t("Authenticate")

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Verified At"),
        help_text=_t("Timestamp when this contact was verified."),
    )

    verification_code = models.CharField(
        max_length=6,
        verbose_name=_t("Verification Code"),
        help_text=_t("The one-time code sent to the user."),
    )

    code_purpose = models.CharField(
        max_length=3,
        choices=CodePurpose.choices,
        verbose_name=_t("Code Purpose"),
        help_text=_t("The operation this code authorizes."),
    )

    code_use_attempts = models.SmallIntegerField(
        default=0,
        verbose_name=_t("Attempts"),
        help_text=_t(
            "Number of failed verification attempts. Negative value means "
            "successful verification."
        ),
    )

    code_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Expires At"),
        help_text=_t("Timestamp when this code expires and becomes invalid."),
    )

    class Meta:
        abstract = True

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_expired(self) -> bool:
        """Whether the current verification code has expired.

        A code is considered expired when no expiration timestamp is set,
        or when the current time is past ``code_expires_at``.

        Returns:
            bool: ``True`` if the code is expired or has no expiration
            set, otherwise ``False``.
        """
        if self.code_expires_at is None:
            return True
        return timezone.now() > self.code_expires_at

    @property
    def max_attempts_reached(self) -> bool:
        """Whether the maximum number of failed attempts has been reached.

        Returns:
            bool: ``True`` if ``code_use_attempts`` is greater than or
            equal to :data:`MAX_ATTEMPTS`, otherwise ``False``.
        """
        return self.code_use_attempts >= MAX_ATTEMPTS

    @property
    def is_verified(self) -> bool:
        """Whether this record has been successfully verified.

        Returns:
            bool: ``True`` if ``verified_at`` is set, otherwise ``False``.
        """
        return self.verified_at is not None

    @property
    def attempts(self) -> int:
        """Absolute number of recorded verification attempts.

        Returns:
            int: The magnitude of ``code_use_attempts``, independent of
            its sign.
        """
        return abs(self.code_use_attempts)

    # ------------------------------------------------------------------
    # Purpose matching
    # ------------------------------------------------------------------

    def matches_purpose(self, purpose: str) -> bool:
        """Whether the current code was issued for ``purpose``.

        A code whose purpose does not match must be rejected outright,
        without consuming an attempt — the caller simply presented a
        code for the wrong operation.

        Args:
            purpose (str): The :class:`CodePurpose` value to check against.

        Returns:
            bool: ``True`` if ``code_purpose`` equals ``purpose``,
            otherwise ``False``.
        """
        return self.code_purpose == purpose

    def is_usable_for(self, purpose: str) -> bool:
        """Whether the current code can be used for ``purpose`` right now.

        A code is usable when it matches ``purpose``, has not expired,
        and has not exhausted its attempt budget.

        Args:
            purpose (str): The :class:`CodePurpose` value to check against.

        Returns:
            bool: ``True`` if the code is usable for ``purpose``,
            otherwise ``False``.
        """
        return (
            self.matches_purpose(purpose)
            and not self.is_expired
            and not self.max_attempts_reached
        )

    # ------------------------------------------------------------------
    # Core code lifecycle
    # ------------------------------------------------------------------

    def refresh_code(
        self,
        purpose: str,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a new purpose-scoped verification code.

        Invalidates any current code state, generates a new six-digit
        code, records ``purpose`` as the operation this code authorizes,
        and sets a new expiration based on ``minutes``.

        Prefer the purpose-specific helpers (e.g.
        :meth:`refresh_change_email_code`) over calling this method
        directly — they prevent accidentally issuing a code for the
        wrong purpose.

        Args:
            purpose (str): The :class:`CodePurpose` value this code
                authorizes. Required — there is no default, so callers
                must be explicit about what the code is for.
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        self.invalidate(save=False)
        self.verification_code = generate_six_digit_code()
        self.code_purpose = purpose
        self.set_expiration(minutes, save=False)

        if save:
            self.save(
                update_fields=[
                    "verification_code",
                    "code_purpose",
                    "code_expires_at",
                    "code_use_attempts",
                ]
            )
        return self.verification_code

    def set_expiration(self, minutes: int, save: bool = True) -> None:
        """Set the expiration timestamp of the current code.

        Args:
            minutes (int): Positive number of minutes from now until the
                code expires.
            save (bool, optional): Whether to persist the change.

        Raises:
            ValidationError: If ``minutes`` is not a positive integer.
        """
        if minutes <= 0:
            raise ValidationError(
                InvalidValue(_t("Minutes must be a positive integer."))
            )

        self.code_expires_at = timezone.now() + timedelta(minutes=minutes)

        if save:
            self.save(update_fields=["code_expires_at"])

    def increment_attempts(self, save: bool = True) -> int:
        """Record a failed verification attempt.

        Increments ``code_use_attempts`` by one based on the current
        absolute attempt count.

        Args:
            save (bool, optional): Whether to persist the change.

        Returns:
            int: The updated value of ``code_use_attempts``.
        """
        self.code_use_attempts = self.attempts + 1

        if save:
            self.save(update_fields=["code_use_attempts"])

        return self.code_use_attempts

    def invalidate(self, save: bool = True) -> None:
        """Reset the current code's expiration and attempt counter.

        Clears ``code_expires_at`` and resets ``code_use_attempts`` to
        zero. The purpose is intentionally left untouched — it is
        overwritten on the next :meth:`refresh_code` call, and keeping
        it makes audit trails clearer.

        Args:
            save (bool, optional): Whether to persist the changes.
        """
        self.code_expires_at = None
        self.code_use_attempts = 0

        if save:
            self.save(update_fields=["code_expires_at", "code_use_attempts"])

    def verify(self, save: bool = True) -> None:
        """Mark this record as successfully verified.

        Sets ``verified_at`` to the current timestamp.

        Args:
            save (bool, optional): Whether to persist the change.
        """
        self.verified_at = timezone.now()
        if save:
            self.save(update_fields=["verified_at"])

    # ------------------------------------------------------------------
    # Purpose-specific helpers
    # ------------------------------------------------------------------

    def refresh_change_contact_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing a contact change.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.CHANGE_CONTACT, minutes=minutes, save=save
        )

    def refresh_remove_contact_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing a contact removal.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.REMOVE_CONTACT, minutes=minutes, save=save
        )

    def refresh_verify_contact_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing initial contact verification.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.VERIFY_CONTACT, minutes=minutes, save=save
        )

    def refresh_reset_password_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing a password reset.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.RESET_PASSWORD, minutes=minutes, save=save
        )

    def refresh_authenticate_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing passwordless authentication.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.AUTHENTICATE, minutes=minutes, save=save
        )


CodePurpose = VerifiableMixin.CodePurpose
