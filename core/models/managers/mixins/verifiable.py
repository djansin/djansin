"""Verifiable manager mixin providing verification-related query methods at the manager level.

This module defines a mixin that adds verification-related filtering capabilities to
model managers. It delegates to the underlying queryset's verification filtering methods
while providing convenient manager-level access to common verification queries.

The mixin is designed to work with models that have verification state tracking with
revocation capabilities. Common use cases include email verification, KYC/AML processes,
document verification, or any workflow requiring multi-state verification.
"""

from typing import Generic, TypeVar

from django.db.models import Q
from django.utils import timezone

from core.models.managers.querysets import BaseQuerySet


BaseQuerySetType = TypeVar("BaseQuerySetType", bound="BaseQuerySet")


class VerifiableManagerMixin(Generic[BaseQuerySetType]):
    """A manager mixin that adds verification-related filtering capabilities.

    This mixin provides manager-level methods for filtering records based on
    their verification lifecycle. It delegates to the queryset's filtering
    methods while maintaining the standard manager interface.

    The verification lifecycle:
    1. PENDING: Initial state, waiting for verification
    2. ACTIVE: Successfully verified and currently valid
    3. REASSIGNED: Reassigned to another verifier or entity
    4. REINSTATED: Reinstated after being previously inactive

    The mixin provides:
    - Status-based filtering (pending, active, reassigned, reinstated)
    - Composite status filters (verified, unverified, revoked, not_revoked)
    - Combined filters (requires_verification, expired_verifications)
    - Counting methods for all verification states
    - Existence checks for all verification states

    This mixin is designed to be used with Django Managers and should be
    combined with VerifiableQuerySetMixin for complete query capabilities.

    Attributes:
        get_queryset: Must be provided by the manager class using this mixin.
            Returns the queryset instance to apply filters on.

        model: The model class using this manager. Must have a VerificationStatus
            enumeration defined on it.

        verification_state: The field storing verification status enumeration.
            Expected to be defined on the model using this mixin.

        verified_at: The DateTimeField storing when verification occurred.
            Expected to be defined on the model using this mixin.

        revoked_at: The DateTimeField storing when verification was revoked.
            Expected to be defined on the model using this mixin.

        VerificationStatus: An enumeration defining the verification states.
            Expected to be defined on the model using this mixin.
    """

    # ========== Core filtering (delegation to queryset) ==========

    def pending(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only pending records.

        Returns:
            A queryset containing only records with PENDING verification status.
        """
        return self.get_queryset().filter(
            verification_state=self.model.VerificationStatus.PENDING
        )

    def active(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only active records.

        Returns:
            A queryset containing only records with ACTIVE verification status.
        """
        return self.get_queryset().filter(
            verification_state=self.model.VerificationStatus.ACTIVE
        )

    def reassigned(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only reassigned records.

        Returns:
            A queryset containing only records with REASSIGNED verification status.
        """
        return self.get_queryset().filter(
            verification_state=self.model.VerificationStatus.REASSIGNED
        )

    def reinstated(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only reinstated records.

        Returns:
            A queryset containing only records with REINSTATED verification status.
        """
        return self.get_queryset().filter(
            verification_state=self.model.VerificationStatus.REINSTATED
        )

    def verified(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only verified records.

        Records are considered verified if they are not pending and not revoked.

        Returns:
            A queryset containing only verified records.
        """
        return self.get_queryset().exclude(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(revoked_at__isnull=False)
        )

    def unverified(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only unverified records.

        Records are considered unverified if they are pending or revoked.

        Returns:
            A queryset containing unverified records (pending or revoked).
        """
        return self.get_queryset().filter(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(revoked_at__isnull=False)
        )

    def revoked(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only revoked records.

        Returns:
            A queryset containing only records with revoked_at not null.
        """
        return self.get_queryset().filter(revoked_at__isnull=False)

    def not_revoked(self) -> BaseQuerySetType:
        """Return a queryset filtered to exclude revoked records.

        Returns:
            A queryset containing records with revoked_at is None.
        """
        return self.get_queryset().filter(revoked_at__isnull=True)

    def requires_verification(self, max_age_days: int = 30) -> BaseQuerySetType:
        """Return a queryset of records that require verification.

        Records requiring verification are those that are pending or have
        expired verification (active records verified beyond max_age_days).

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            A queryset containing records needing verification.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_age_days)
        return self.get_queryset().filter(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(
                verified_at__isnull=False,
                verified_at__lt=cutoff,
                revoked_at__isnull=True,
            )
        )

    def expired_verifications(self, max_age_days: int = 30) -> BaseQuerySetType:
        """Return a queryset of verified records with expired verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            A queryset containing verified records with expired verification.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_age_days)
        return self.verified().filter(verified_at__lt=cutoff)

    # ========== Count methods ==========

    def count_pending(self) -> int:
        """Count pending records.

        Returns:
            The total count of records with PENDING verification status.
        """
        return self.pending().count()

    def count_active(self) -> int:
        """Count active records.

        Returns:
            The total count of records with ACTIVE verification status.
        """
        return self.active().count()

    def count_reassigned(self) -> int:
        """Count reassigned records.

        Returns:
            The total count of records with REASSIGNED verification status.
        """
        return self.reassigned().count()

    def count_reinstated(self) -> int:
        """Count reinstated records.

        Returns:
            The total count of records with REINSTATED verification status.
        """
        return self.reinstated().count()

    def count_revoked(self) -> int:
        """Count revoked records.

        Returns:
            The total count of records with revoked_at not null.
        """
        return self.revoked().count()

    def count_expired_verification(self, max_age_days: int = 30) -> int:
        """Count records with expired verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            The count of records with expired verification.
        """
        return self.expired_verifications(max_age_days).count()

    def count_requires_verification(self) -> int:
        """Count records that require verification.

        Returns:
            The count of records requiring verification.
        """
        return self.requires_verification().count()

    # ========== Existence checks ==========

    def exists_pending(self) -> bool:
        """Check if any pending records exist.

        Returns:
            True if at least one pending record exists, False otherwise.
        """
        return self.pending().exists()

    def exists_active(self) -> bool:
        """Check if any active records exist.

        Returns:
            True if at least one active record exists, False otherwise.
        """
        return self.active().exists()

    def exists_reassigned(self) -> bool:
        """Check if any reassigned records exist.

        Returns:
            True if at least one reassigned record exists, False otherwise.
        """
        return self.reassigned().exists()

    def exists_reinstated(self) -> bool:
        """Check if any reinstated records exist.

        Returns:
            True if at least one reinstated record exists, False otherwise.
        """
        return self.reinstated().exists()

    def exists_revoked(self) -> bool:
        """Check if any revoked records exist.

        Returns:
            True if at least one revoked record exists, False otherwise.
        """
        return self.revoked().exists()
