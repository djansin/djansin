"""Verifiable query set mixin providing filtering and query utilities for verifiable models.

This module defines a mixin that adds verification-related filtering capabilities to
query sets. It provides comprehensive methods for filtering records based on their
verification state, revocation status, and various time-based queries.

The mixin is designed to work with models that have:
- `verification_state`: An enumeration field tracking the verification lifecycle
- `verified_at`: A timestamp field recording when verification occurred
- `revoked_at`: A nullable timestamp field tracking when verification was revoked
- `created_at`: A timestamp field for tracking record creation

Common use cases include email verification, KYC/AML processes, document verification,
or any workflow requiring multi-state verification with revocation capabilities.
"""

from datetime import datetime
from typing import Self

from django.db.models import Q
from django.utils import timezone


class VerifiableQuerySetMixin:
    """A mixin that adds verification-related filtering capabilities to query sets.

    This mixin provides a comprehensive set of methods for querying records
    based on their verification lifecycle. It assumes the model has a
    VerificationStatus enumeration with states: PENDING, ACTIVE, REASSIGNED,
    REINSTATED, and fields for tracking verification and revocation timestamps.

    The verification lifecycle:
    1. PENDING: Initial state, waiting for verification
    2. ACTIVE: Successfully verified and currently valid
    3. REASSIGNED: Reassigned to another verifier or entity
    4. REINSTATED: Reinstated after being previously inactive

    The mixin provides:
    - Status-based filtering (pending, active, reassigned, reinstated)
    - Composite status filters (verified, unverified, revoked, not_revoked)
    - Time-based verification queries (verified_before, verified_today, etc.)
    - Time-based revocation queries (revoked_before, revoked_today, etc.)
    - Combined filters (verified_and_active, requires_verification)
    - Existence checks and counting methods
    - Utility methods for cleanup and ordering

    This mixin is designed to be used with Django QuerySets and can be combined
    with other query set mixins for comprehensive query capabilities.

    Attributes:
        verification_state: The field storing verification status enumeration.
            Expected to be defined on the model using this mixin.

        verified_at: The DateTimeField storing when verification occurred.
            Expected to be defined on the model using this mixin.

        revoked_at: The DateTimeField storing when verification was revoked.
            Expected to be defined on the model using this mixin.

        created_at: The DateTimeField storing when the record was created.
            Expected to be defined on the model using this mixin.

        VerificationStatus: An enumeration defining the verification states.
            Expected to be defined on the model using this mixin.
    """

    # ========== Status-based filtering ==========

    def pending(self) -> Self:
        """Filter the queryset to include only records with PENDING verification status.

        Returns:
            A filtered queryset containing only pending records.
        """
        return self.filter(verification_state=self.model.VerificationStatus.PENDING)

    def active(self) -> Self:
        """Filter the queryset to include only records with ACTIVE verification status.

        Returns:
            A filtered queryset containing only active records.
        """
        return self.filter(verification_state=self.model.VerificationStatus.ACTIVE)

    def reassigned(self) -> Self:
        """Filter the queryset to include only records with REASSIGNED verification status.

        Returns:
            A filtered queryset containing only reassigned records.
        """
        return self.filter(verification_state=self.model.VerificationStatus.REASSIGNED)

    def reinstated(self) -> Self:
        """Filter the queryset to include only records with REINSTATED verification status.

        Returns:
            A filtered queryset containing only reinstated records.
        """
        return self.filter(verification_state=self.model.VerificationStatus.REINSTATED)

    def verified(self) -> Self:
        """Filter the queryset to include only verified records.

        Records are considered verified if they are not pending and not revoked.

        Returns:
            A filtered queryset containing verified records (active, reassigned,
            or reinstated with no revocation).
        """
        return self.exclude(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(revoked_at__isnull=False)
        )

    def unverified(self) -> Self:
        """Filter the queryset to include only unverified records.

        Records are considered unverified if they are pending or revoked.

        Returns:
            A filtered queryset containing unverified records (pending or revoked).
        """
        return self.filter(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(revoked_at__isnull=False)
        )

    def revoked(self) -> Self:
        """Filter the queryset to include revoked records.

        Returns:
            A filtered queryset containing records where revoked_at is not None.
        """
        return self.filter(revoked_at__isnull=False)

    def not_revoked(self) -> Self:
        """Filter the queryset to exclude revoked records.

        Returns:
            A filtered queryset containing records with revoked_at is None.
        """
        return self.filter(revoked_at__isnull=True)

    def verifiable(self) -> Self:
        """Filter the queryset to include only records that can be verified.

        Records that can be verified are those with PENDING status.

        Returns:
            A filtered queryset containing verifiable records.
        """
        return self.pending()

    def revokable(self) -> Self:
        """Filter the queryset to include only records that can be revoked.

        Records that can be revoked are those that are verified.

        Returns:
            A filtered queryset containing revokable records.
        """
        return self.verified()

    # ========== Time-based filtering (verification) ==========

    def verified_before(self, timestamp: datetime) -> Self:
        """Filter verified records with verification before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with verified_at
                before this time will be included.

        Returns:
            A filtered queryset of verified records with verified_at < timestamp.
        """
        return self.verified().filter(verified_at__lt=timestamp)

    def verified_after(self, timestamp: datetime) -> Self:
        """Filter verified records with verification after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with verified_at
                after this time will be included.

        Returns:
            A filtered queryset of verified records with verified_at > timestamp.
        """
        return self.verified().filter(verified_at__gt=timestamp)

    def verified_between(self, start: datetime, end: datetime) -> Self:
        """Filter verified records within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset of verified records with verified_at between
            start and end.
        """
        return self.verified().filter(verified_at__gte=start, verified_at__lte=end)

    def verified_within_days(self, days: int) -> Self:
        """Filter verified records within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset of verified records with verified_at within
            the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.verified().filter(verified_at__gte=cutoff)

    def verified_today(self) -> Self:
        """Filter verified records verified today.

        Returns:
            A filtered queryset of verified records with verified_at date
            equal to today.
        """
        today = timezone.now().date()
        return self.verified().filter(verified_at__date=today)

    def never_verified(self) -> Self:
        """Filter records that have never been verified.

        Returns:
            A filtered queryset containing records with verified_at is None.
        """
        return self.filter(verified_at__isnull=True)

    # ========== Time-based filtering (revocation) ==========

    def revoked_before(self, timestamp: datetime) -> Self:
        """Filter records revoked before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with revoked_at
                before this time will be included.

        Returns:
            A filtered queryset with revoked_at < timestamp.
        """
        return self.filter(revoked_at__lt=timestamp)

    def revoked_after(self, timestamp: datetime) -> Self:
        """Filter records revoked after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with revoked_at
                after this time will be included.

        Returns:
            A filtered queryset with revoked_at > timestamp.
        """
        return self.filter(revoked_at__gt=timestamp)

    def revoked_between(self, start: datetime, end: datetime) -> Self:
        """Filter records revoked within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset with revoked_at between start and end.
        """
        return self.filter(revoked_at__gte=start, revoked_at__lte=end)

    def revoked_within_days(self, days: int) -> Self:
        """Filter records revoked within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset with revoked_at within the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(revoked_at__gte=cutoff)

    def revoked_today(self) -> Self:
        """Filter records revoked today.

        Returns:
            A filtered queryset with revoked_at date equal to today.
        """
        today = timezone.now().date()
        return self.filter(revoked_at__date=today)

    def never_revoked(self) -> Self:
        """Filter records that have never been revoked.

        Returns:
            A filtered queryset containing records with revoked_at is None.
        """
        return self.filter(revoked_at__isnull=True)

    # ========== Combined filters ==========

    def verified_and_active(self) -> Self:
        """Filter records that are verified and not revoked.

        Returns:
            A filtered queryset containing verified records that are not revoked.
        """
        return self.verified().never_revoked()

    def requires_verification(self, max_age_days: int = 30) -> Self:
        """Filter records that require verification.

        Records requiring verification are those that are pending or have
        expired verification (active records verified beyond max_age_days).

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            A filtered queryset containing records needing verification.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_age_days)
        return self.filter(
            Q(verification_state=self.model.VerificationStatus.PENDING)
            | Q(
                verified_at__isnull=False,
                verified_at__lt=cutoff,
                revoked_at__isnull=True,
            )
        )

    def expired_verifications(self, max_age_days: int = 30) -> Self:
        """Filter verified records with expired verification.

        Records with ACTIVE status that have exceeded the maximum allowed
        age since verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            A filtered queryset containing verified records with expired
            verification.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_age_days)
        return self.verified().filter(verified_at__lt=cutoff)

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

    def exists_verified(self) -> bool:
        """Check if any verified records exist.

        Returns:
            True if at least one verified record exists, False otherwise.
        """
        return self.verified().exists()

    def exists_revoked(self) -> bool:
        """Check if any revoked records exist.

        Returns:
            True if at least one revoked record exists, False otherwise.
        """
        return self.filter(revoked_at__isnull=False).exists()

    def exists_requires_verification(self, max_age_days: int = 30) -> bool:
        """Check if any records require verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            True if at least one record requires verification, False otherwise.
        """
        return self.requires_verification(max_age_days).exists()

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

    def count_verified(self) -> int:
        """Count verified records.

        Returns:
            The total count of verified records.
        """
        return self.verified().count()

    def count_unverified(self) -> int:
        """Count unverified records.

        Returns:
            The total count of unverified records (pending or revoked).
        """
        return self.unverified().count()

    def count_revoked(self) -> int:
        """Count revoked records.

        Returns:
            The total count of records with revoked_at not null.
        """
        return self.filter(revoked_at__isnull=False).count()

    def count_verified_and_active(self) -> int:
        """Count records that are both verified and not revoked.

        Returns:
            The total count of verified records that are not revoked.
        """
        return self.verified_and_active().count()

    def count_requires_verification(self, max_age_days: int = 30) -> int:
        """Count records that require verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            The count of records requiring verification.
        """
        return self.requires_verification(max_age_days).count()

    def count_expired_verifications(self, max_age_days: int = 30) -> int:
        """Count verified records with expired verification.

        Args:
            max_age_days: Maximum age of verification in days. Defaults to 30.

        Returns:
            The count of verified records with expired verification.
        """
        return self.expired_verifications(max_age_days).count()

    # ========== Utility methods ==========

    def pending_older_than(self, days: int) -> Self:
        """Filter pending records older than a specified number of days.

        This method is useful for identifying stale pending records that may
        need to be cleaned up or escalated.

        Args:
            days: The age threshold in days.

        Returns:
            A filtered queryset of pending records with created_at older
            than the specified days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.pending().filter(created_at__lt=cutoff)

    def ready_for_cleanup(self, max_pending_days: int = 30) -> Self:
        """Filter records ready for cleanup.

        This method identifies records that can be removed or archived:
        - Pending records older than max_pending_days
        - All revoked records

        Args:
            max_pending_days: Maximum days a pending record can exist before
                being considered for cleanup. Defaults to 30.

        Returns:
            A filtered queryset containing records ready for cleanup.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_pending_days)
        return self.filter(
            Q(
                verification_state=self.model.VerificationStatus.PENDING,
                created_at__lt=cutoff,
            )
            | Q(revoked_at__isnull=False)
        )

    def order_by_verification_status(self) -> Self:
        """Order records by verification status.

        Returns:
            An ordered queryset by verification_state ascending.
        """
        return self.order_by("verification_state")

    def order_by_verification_age(self, descending: bool = True) -> Self:
        """Order verified records by verification age.

        Args:
            descending: If True, order newest first. Defaults to True.

        Returns:
            An ordered queryset of verified records by verified_at.
        """
        order = "-verified_at" if descending else "verified_at"
        return self.filter(verified_at__isnull=False).order_by(order)
