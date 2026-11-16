"""Reusable mixin providing one-time verification code behavior.

This module defines :class:`VerifiableMixin`, an abstract model mixin that
adds state and behavior for issuing, expiring, validating, and consuming
one-time verification codes. It is intended to be mixed into contact-like
models (e.g. ``Email``, ``Phone``) that require proof of ownership through
a short-lived numeric code.

Module-level constants:
    MAX_ATTEMPTS (int): Maximum number of failed verification attempts
        allowed before a code is considered unusable.
    DEFAULT_CODE_TTL_MINUTES (int): Default time-to-live, in minutes, for a
        freshly issued verification code.
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
    """Abstract mixin adding one-time verification code state and behavior.

    Provides persisted fields for tracking the verification lifecycle
    (verification timestamp, current code, failed attempt count, and
    expiration timestamp) along with chainable helper methods to refresh,
    expire, increment, invalidate, and mark a code as verified.

    Subclasses are expected to be concrete Django models. This mixin does
    not declare a ``Meta`` other than ``abstract = True``.

    Attributes:
        verified_at (datetime.datetime | None): Timestamp when the contact
            was successfully verified, or ``None`` if not yet verified.
        verification_code (str): The current one-time code associated with
            this record. Maximum length is 6 characters.
        code_use_attempts (int): Signed counter of verification attempts.
            Positive values represent failed attempts; a negative value
            marks a successful verification.
        code_expires_at (datetime.datetime | None): Timestamp at which the
            current code becomes invalid, or ``None`` when the code has
            been invalidated.
    """

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

    code_use_attempts = models.SmallIntegerField(
        default=0,
        verbose_name=_t("Attempts"),
        help_text=_t(
            "Number of failed verification attempts. Negative value means successful verification."
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

    @property
    def is_expired(self) -> bool:
        """Whether the current verification code has expired.

        A code is considered expired when no expiration timestamp is set,
        or when the current time is past ``code_expires_at``.

        Returns:
            bool: ``True`` if the code is expired or has no expiration set,
            otherwise ``False``.
        """
        if self.code_expires_at is None:
            return True
        return timezone.now() > self.code_expires_at

    @property
    def max_attempts_reached(self) -> bool:
        """Whether the maximum number of failed attempts has been reached.

        Returns:
            bool: ``True`` if ``code_use_attempts`` is greater than or equal
            to :data:`MAX_ATTEMPTS`, otherwise ``False``.
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
            int: The magnitude of ``code_use_attempts``, independent of its
            sign.
        """
        return abs(self.code_use_attempts)

    def refresh_code(
        self, minutes: int = DEFAULT_CODE_TTL_MINUTES, save: bool = True
    ) -> str:
        """Issue a new verification code with a fresh expiration window.

        Invalidates any current code state, generates a new six-digit code,
        and sets a new expiration based on ``minutes``. When ``save`` is
        ``True``, persists only the affected fields.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes. Defaults
                to ``True``.

        Returns:
            str: The newly generated verification code.
        """
        self.invalidate(save=False)
        self.verification_code = generate_six_digit_code()
        self.set_expiration(minutes, save=False)

        if save:
            self.save(
                update_fields=[
                    "verification_code",
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
            save (bool, optional): Whether to persist the change. Defaults
                to ``True``.

        Raises:
            ValidationError: If ``minutes`` is not a positive integer (wraps
                :class:`~core.exceptions.errors.validation.InvalidValue`).
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
            save (bool, optional): Whether to persist the change. Defaults
                to ``True``.

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
        zero, effectively marking the code as unusable until refreshed.

        Args:
            save (bool, optional): Whether to persist the changes. Defaults
                to ``True``.
        """
        self.code_expires_at = None
        self.code_use_attempts = 0

        if save:
            self.save(update_fields=["code_expires_at", "code_use_attempts"])

    def verify(self, save: bool = True) -> None:
        """Mark this record as successfully verified.

        Sets ``verified_at`` to the current timestamp.

        Args:
            save (bool, optional): Whether to persist the change. Defaults
                to ``True``.
        """
        self.verified_at = timezone.now()
        if save:
            self.save(update_fields=["verified_at"])
