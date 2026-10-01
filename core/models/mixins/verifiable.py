"""Django model mixin providing comprehensive verification workflow functionality.

This module provides a mixin that implements a complete verification workflow
with multiple states (pending, active, reassigned, reinstated) and revocation
tracking for models that require verification processes.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions.common import BusinessError
from core.exceptions.errors.business import (
    InvalidStateForVerification,
    RecordAlreadyVerified,
)
from core.models.mixins.abstract import AbstractModelMixin


class VerifiableMixin(AbstractModelMixin):
    """Mixin that adds comprehensive verification workflow capabilities to a model.

    This mixin implements a state machine for verification workflows with
    four states:
    - PENDING: Initial state, awaiting verification
    - ACTIVE: Successfully verified and active
    - REASSIGNED: Verification has been reassigned
    - REINSTATED: Verification has been reinstated

    Additionally, records can be revoked (revoked_at set), which is tracked
    separately from the verification state.

    Features include:
    - State management with validation
    - Verification, reassignment, reinstatement, and revocation operations
    - Status checking properties
    - Age calculations for verification timestamps
    - Validation methods for business logic

    Attributes:
        verification_state: CharField indicating the current verification state.
        verified_at: DateTimeField timestamp of when the record was verified.
        revoked_at: DateTimeField timestamp of when the record was revoked.
        created_at: Timestamp of object creation (inherited).
        updated_at: Timestamp of last object update (inherited).
    """

    class VerificationStatus(models.TextChoices):
        """Available verification status choices."""

        PENDING = "pen", _t("Pending")
        ACTIVE = "act", _t("Active")
        REASSIGNED = "ras", _t("Reassigned")
        REINSTATED = "rin", _t("Reinstated")

    verification_state = models.CharField(
        max_length=3,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        verbose_name=_t("Verification Status"),
        help_text=_t(
            "Current verification state: pending, active, reassigned, or revoked."
        ),
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Verified At"),
        help_text=_t("Timestamp when the record was successfully verified."),
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Revoked At"),
        help_text=_t("Timestamp when the record was revoked."),
    )

    class Meta:
        """Metadata configuration for VerifiableMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides verification fields to all inheriting models.
        """

        abstract = True

    # ========== Class Methods ==========

    @classmethod
    def get_verification_status_choices(cls) -> list[tuple[str, str]]:
        """Get the verification status choices.

        Returns:
            A list of (code, display_name) tuples for the verification status.
        """
        return cls.VerificationStatus.choices

    @classmethod
    def get_default_status(cls) -> str:
        """Get the default verification status.

        Returns:
            The default status code (PENDING).
        """
        return cls.VerificationStatus.PENDING

    # ========== Properties ==========

    @property
    def is_pending(self) -> bool:
        """Check if the record is in PENDING state.

        Returns:
            True if verification_state is PENDING, False otherwise.
        """
        return self.verification_state == self.VerificationStatus.PENDING

    @property
    def is_active(self) -> bool:
        """Check if the record is in ACTIVE state.

        Returns:
            True if verification_state is ACTIVE, False otherwise.
        """
        return self.verification_state == self.VerificationStatus.ACTIVE

    @property
    def is_reassigned(self) -> bool:
        """Check if the record is in REASSIGNED state.

        Returns:
            True if verification_state is REASSIGNED, False otherwise.
        """
        return self.verification_state == self.VerificationStatus.REASSIGNED

    @property
    def is_reinstated(self) -> bool:
        """Check if the record is in REINSTATED state.

        Returns:
            True if verification_state is REINSTATED, False otherwise.
        """
        return self.verification_state == self.VerificationStatus.REINSTATED

    @property
    def is_revoked(self) -> bool:
        """Check if the record has been revoked.

        Returns:
            True if revoked_at is not None, False otherwise.
        """
        return self.revoked_at is not None

    @property
    def is_verified(self) -> bool:
        """Check if the record is verified.

        A record is considered verified if it is not revoked and not pending.

        Returns:
            True if the record is verified, False otherwise.
        """
        return not self.is_revoked and not self.is_pending

    @property
    def is_verifiable(self) -> bool:
        """Check if the record can be verified.

        Returns:
            True if the record is in PENDING state, False otherwise.
        """
        return self.is_pending

    @property
    def is_reassignable(self) -> bool:
        """Check if the record can be reassigned.

        Returns:
            True if the record is in PENDING state, False otherwise.
        """
        return self.is_pending

    @property
    def is_reinstatable(self) -> bool:
        """Check if the record can be reinstated.

        Returns:
            True if the record is in PENDING state, False otherwise.
        """
        return self.is_pending

    @property
    def is_revokable(self) -> bool:
        """Check if the record can be revoked.

        Returns:
            True if the record is verified, False otherwise.
        """
        return self.is_verified

    @property
    def verification_age_days(self) -> int | None:
        """Get the age of verification in days.

        Returns:
            The number of days since verification, or None if not verified.
        """
        if not self.verified_at:
            return None
        delta = timezone.now() - self.verified_at
        return delta.days

    @property
    def verification_age_hours(self) -> float | None:
        """Get the age of verification in hours.

        Returns:
            The number of hours since verification, or None if not verified.
        """
        if not self.verified_at:
            return None
        delta = timezone.now() - self.verified_at
        return delta.total_seconds() / 3600

    @property
    def revocation_age_days(self) -> int | None:
        """Get the age of revocation in days.

        Returns:
            The number of days since revocation, or None if not revoked.
        """
        if not self.revoked_at:
            return None
        delta = timezone.now() - self.revoked_at
        return delta.days

    @property
    def revocation_age_hours(self) -> int | None:
        """Get the age of revocation in hours.

        Returns:
            The number of hours since revocation, or None if not revoked.
        """
        if not self.revoked_at:
            return None
        delta = timezone.now() - self.revoked_at
        return delta.total_seconds() / 3600

    # ========== Verification Methods ==========

    def verify(self) -> None:
        """Verify the record, transitioning from PENDING to ACTIVE.

        This method marks the record as verified by setting the state to ACTIVE
        and recording the verification timestamp.

        Raises:
            BusinessError: If the record is already active or cannot be verified.
        """
        if self.is_active:
            raise BusinessError(RecordAlreadyVerified())

        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(pk=self.pk, verification_state=self.VerificationStatus.PENDING)
            .update(
                verification_state=self.VerificationStatus.ACTIVE,
                verified_at=timezone.now(),
            )
        )

        if updated_count == 0:
            raise BusinessError(InvalidStateForVerification(next_state=_t("ACTIVE")))

    def reassign(self) -> None:
        """Reassign the verification, transitioning from PENDING to REASSIGNED.

        This method reassigns the verification by setting the state to REASSIGNED
        and recording the verification timestamp.

        Raises:
            BusinessError: If the record is already active or cannot be reassigned.
        """
        if self.is_active:
            raise BusinessError(RecordAlreadyVerified())

        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(pk=self.pk, verification_state=self.VerificationStatus.PENDING)
            .update(
                verification_state=self.VerificationStatus.REASSIGNED,
                verified_at=timezone.now(),
            )
        )

        if updated_count == 0:
            raise BusinessError(
                InvalidStateForVerification(next_state=_t("REASSIGNED"))
            )

    def reinstate(self) -> None:
        """Reinstate the verification, transitioning from PENDING to REINSTATED.

        This method reinstates the verification by setting the state to REINSTATED
        and recording the verification timestamp.

        Raises:
            BusinessError: If the record is already active or cannot be reinstated.
        """
        if self.is_active:
            raise BusinessError(RecordAlreadyVerified())

        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(pk=self.pk, verification_state=self.VerificationStatus.PENDING)
            .update(
                verification_state=self.VerificationStatus.REINSTATED,
                verified_at=timezone.now(),
            )
        )

        if updated_count == 0:
            raise BusinessError(
                InvalidStateForVerification(next_state=_t("REINSTATED"))
            )

    def revoke(self) -> None:
        """Revoke the verification.

        This method revokes the record by setting revoked_at to the current
        timestamp. It only operates on records that are not pending and not
        already revoked.

        Raises:
            BusinessError: If the record is pending or already revoked.
        """
        if self.is_active:
            raise BusinessError(RecordAlreadyVerified())

        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(pk=self.pk)
            .exclude(
                models.Q(verification_state=self.VerificationStatus.PENDING)
                | models.Q(revoked_at__isnull=False),
            )
            .update(revoked_at=timezone.now())
        )

        if updated_count == 0:
            raise BusinessError(InvalidStateForVerification(next_state=_t("REVOKE")))

    # ========== Validation Methods ==========

    def requires_verification(self, max_age_days: int = 30) -> bool:
        """Check if the record requires verification.

        A record requires verification if it is not verified or if its
        verification has expired based on the maximum age.

        Args:
            max_age_days: Maximum allowed age of verification in days.
                Defaults to 30.

        Returns:
            True if the record requires verification, False otherwise.
        """
        if not self.is_verified:
            return True

        delta = timezone.now() - self.verified_at
        return self.is_pending or delta.days > max_age_days

    def is_verified_within(self, days: int) -> bool:
        """Check if the record was verified within the specified number of days.

        Args:
            days: The number of days to check against.

        Returns:
            True if the record is verified and the verification age is within
            the specified days, False otherwise.
        """
        if not self.is_verified:
            return False

        delta = timezone.now() - self.verified_at
        return delta.days <= days

    def was_revoked_within(self, days: int) -> bool:
        """Check if the record was revoked within the specified number of days.

        Args:
            days: The number of days to check against.

        Returns:
            True if the record is revoked and the revocation age is within
            the specified days, False otherwise.
        """
        if not self.is_revoked:
            return False

        delta = timezone.now() - self.revoked_at
        return delta.days <= days
