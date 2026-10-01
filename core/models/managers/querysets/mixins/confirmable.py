"""Confirmable query set mixin providing filtering and query utilities for confirmable models.

This module defines a mixin that adds confirmation-related filtering capabilities to
query sets. It provides methods for filtering records based on their confirmation
status (confirmed/unconfirmed), interaction timestamps (last_confirmed_at), and
various existence and counting utilities.

The mixin is designed to work with models that have `confirmed_at` and
`last_confirmed_at` timestamp fields, commonly used for email verification,
OTP validation, or any workflow requiring user confirmation.
"""

from datetime import datetime
from typing import Self

from django.utils import timezone


class ConfirmableQuerySetMixin:
    """A mixin that adds confirmation-related filtering capabilities to query sets.

    This mixin provides a comprehensive set of methods for querying records
    based on their confirmation status and interaction history. It assumes the
    model has:
    - `confirmed_at`: DateTimeField storing when the record was confirmed
    - `last_confirmed_at`: DateTimeField storing when the last interaction occurred

    The mixin provides:
    - Status-based filtering (confirmed, unconfirmed)
    - Time-based interaction queries (interacted_before, interacted_within_days, etc.)
    - Time-based confirmation queries (confirmed_before, confirmed_today, etc.)
    - Combined filters (expired_interactions)
    - Existence checks and counting methods
    - Cleanup utilities for unconfirmed records

    This mixin is designed to be used with Django QuerySets and can be combined
    with other query set mixins for comprehensive query capabilities.

    Attributes:
        confirmed_at: The DateTimeField used to determine confirmation status.
            Expected to be defined on the model using this mixin.

        last_confirmed_at: The DateTimeField tracking the last interaction time.
            Expected to be defined on the model using this mixin.

        created_at: The DateTimeField tracking creation time (for cleanup utilities).
            Expected to be defined on the model using this mixin.
    """

    # ========== Status-based filtering ==========

    def confirmed(self) -> Self:
        """Filter the queryset to include only confirmed records.

        Returns:
            A filtered queryset containing only records where confirmed_at is not None.
        """
        return self.filter(confirmed_at__isnull=False)

    def unconfirmed(self) -> Self:
        """Filter the queryset to include only unconfirmed records.

        Returns:
            A filtered queryset containing only records where confirmed_at is None.
        """
        return self.filter(confirmed_at__isnull=True)

    # ========== Time-based filtering (interaction) ==========

    def interacted_before(self, timestamp: datetime) -> Self:
        """Filter records with last interaction before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with last_confirmed_at
                before this time will be included.

        Returns:
            A filtered queryset with last_confirmed_at < timestamp.
        """
        return self.filter(last_confirmed_at__lt=timestamp)

    def interacted_after(self, timestamp: datetime) -> Self:
        """Filter records with last interaction after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with last_confirmed_at
                after this time will be included.

        Returns:
            A filtered queryset with last_confirmed_at > timestamp.
        """
        return self.filter(last_confirmed_at__gt=timestamp)

    def interacted_between(self, start: datetime, end: datetime) -> Self:
        """Filter records with last interaction within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset with last_confirmed_at between start and end.
        """
        return self.filter(last_confirmed_at__gte=start, last_confirmed_at__lte=end)

    def interacted_within_days(self, days: int) -> Self:
        """Filter records with last interaction within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset with last_confirmed_at within the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(last_confirmed_at__gte=cutoff)

    def interacted_today(self) -> Self:
        """Filter records with last interaction today.

        Returns:
            A filtered queryset with last_confirmed_at date equal to today.
        """
        today = timezone.now().date()
        return self.filter(last_confirmed_at__date=today)

    def never_interacted(self) -> Self:
        """Filter records that have never had a confirmed interaction.

        Returns:
            A filtered queryset containing records with last_confirmed_at is None.
        """
        return self.filter(last_confirmed_at__isnull=True)

    # ========== Time-based filtering (confirmation) ==========

    def confirmed_before(self, timestamp: datetime) -> Self:
        """Filter records confirmed before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with confirmed_at
                before this time will be included.

        Returns:
            A filtered queryset with confirmed_at < timestamp.
        """
        return self.filter(confirmed_at__lt=timestamp)

    def confirmed_after(self, timestamp: datetime) -> Self:
        """Filter records confirmed after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Records with confirmed_at
                after this time will be included.

        Returns:
            A filtered queryset with confirmed_at > timestamp.
        """
        return self.filter(confirmed_at__gt=timestamp)

    def confirmed_between(self, start: datetime, end: datetime) -> Self:
        """Filter records confirmed within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset with confirmed_at between start and end.
        """
        return self.filter(confirmed_at__gte=start, confirmed_at__lte=end)

    def confirmed_within_days(self, days: int) -> Self:
        """Filter records confirmed within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset with confirmed_at within the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(confirmed_at__gte=cutoff)

    def confirmed_today(self) -> Self:
        """Filter records confirmed today.

        Returns:
            A filtered queryset with confirmed_at date equal to today.
        """
        today = timezone.now().date()
        return self.filter(confirmed_at__date=today)

    def never_confirmed(self) -> Self:
        """Filter records that have never been confirmed.

        Returns:
            A filtered queryset containing records with confirmed_at is None.
        """
        return self.filter(confirmed_at__isnull=True)

    # ========== Combined status filters ==========

    def expired_interactions(self, max_age_days: int = 60) -> Self:
        """Filter records whose last interaction has expired.

        This method is useful for enforcing inactivity policies (e.g., the
        2-month rule for OTP login) where records that haven't been interacted
        with for a certain period should be considered expired.

        Args:
            max_age_days: Maximum age of last interaction in days. Records with
                last_confirmed_at older than this are considered expired.
                Defaults to 60 days.

        Returns:
            A filtered queryset with last_confirmed_at older than max_age_days
            or never interacted.
        """
        cutoff = timezone.now() - timezone.timedelta(days=max_age_days)
        return self.filter(last_confirmed_at__lt=cutoff)

    # ========== Existence checks ==========

    def exists_confirmed(self) -> bool:
        """Check if any confirmed records exist.

        Returns:
            True if at least one confirmed record exists, False otherwise.
        """
        return self.confirmed().exists()

    # ========== Count methods ==========

    def count_confirmed(self) -> int:
        """Count confirmed records.

        Returns:
            The total count of records where confirmed_at is not None.
        """
        return self.confirmed().count()

    def count_unconfirmed(self) -> int:
        """Count unconfirmed records.

        Returns:
            The total count of records where confirmed_at is None.
        """
        return self.unconfirmed().count()

    def count_expired_interactions(self, max_age_days: int = 60) -> int:
        """Count records with expired interactions.

        Args:
            max_age_days: Maximum age of last interaction in days. Defaults to 60.

        Returns:
            The count of records with expired interactions.
        """
        return self.expired_interactions(max_age_days).count()

    def count_interacted_within_days(self, days: int) -> int:
        """Count records with interactions within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of records with interactions within the specified period.
        """
        return self.interacted_within_days(days).count()

    # ========== Utility methods ==========

    def ready_for_cleanup(self, confirmation_expiry_days: int = 30) -> Self:
        """Filter records ready for cleanup.

        This method returns unconfirmed records that are older than the
        specified expiry days, making them candidates for cleanup operations.

        Args:
            confirmation_expiry_days: Age threshold for unconfirmed records.
                Records created before this many days ago are considered
                ready for cleanup. Defaults to 30 days.

        Returns:
            A filtered queryset of unconfirmed records older than expiry days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=confirmation_expiry_days)
        return self.unconfirmed().filter(created_at__lt=cutoff)
