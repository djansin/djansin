"""Blockable query set mixin providing filtering and query utilities for blockable models.

This module defines a mixin that adds block-related filtering capabilities to
query sets. It provides methods for filtering records based on their block
status (blocked/not blocked), block expiration times, and various existence
and counting utilities.

The mixin is designed to work with models that have a `blocked_until` timestamp
field, where a record is considered blocked if `blocked_until` is in the future.
"""

from datetime import datetime
from typing import Self

from django.db.models import Q
from django.utils import timezone


class BlockableQuerySetMixin:
    """A mixin that adds block-related filtering capabilities to query sets.

    This mixin provides a comprehensive set of methods for querying records
    based on their block status. It assumes the model has a `blocked_until`
    DateTimeField that stores the timestamp when the block expires.

    A record is considered:
    - Blocked: If `blocked_until` is in the future (blocked_until > now)
    - Not blocked: If `blocked_until` is null or in the past (blocked_until <= now)

    The mixin provides:
    - Status-based filtering (blocked, not_blocked)
    - Time-based block expiration queries (blocked_before, blocked_after, etc.)
    - Existence checks (exists_blocked)
    - Counting methods (count_blocked, count_not_blocked)

    This mixin is designed to be used with Django QuerySets and can be combined
    with other query set mixins for comprehensive query capabilities.

    Attributes:
        blocked_until: The DateTimeField used to determine block status.
            Expected to be defined on the model using this mixin.
    """

    # ========== Status-based filtering ==========

    def blocked(self) -> Self:
        """Filter the queryset to include only currently blocked records.

        A record is considered blocked if its `blocked_until` timestamp is
        in the future relative to the current time.

        Returns:
            A filtered queryset containing records with blocked_until > now.
        """
        return self.filter(blocked_until__gt=timezone.now())

    def not_blocked(self) -> Self:
        """Filter the queryset to exclude currently blocked records.

        A record is considered not blocked if its `blocked_until` timestamp
        is null or in the past relative to the current time.

        Returns:
            A filtered queryset containing records that are not currently
            blocked (blocked_until is null or <= now).
        """
        return self.filter(
            Q(blocked_until__isnull=True) | Q(blocked_until__lte=timezone.now())
        )

    # ========== Block-based filtering ==========

    def blocked_before(self, timestamp: datetime) -> Self:
        """Filter records whose block expires before a specific timestamp.

        This method filters records that are blocked with a `blocked_until`
        timestamp before the given timestamp.

        Args:
            timestamp: The datetime threshold. Records with blocked_until
                before this time will be included.

        Returns:
            A filtered queryset of records with blocked_until < timestamp.
        """
        return self.filter(blocked_until__lt=timestamp)

    def blocked_after(self, timestamp: datetime) -> Self:
        """Filter records whose block expires after a specific timestamp.

        This method filters records that are blocked with a `blocked_until`
        timestamp after the given timestamp.

        Args:
            timestamp: The datetime threshold. Records with blocked_until
                after this time will be included.

        Returns:
            A filtered queryset of records with blocked_until > timestamp.
        """
        return self.filter(blocked_until__gt=timestamp)

    def blocked_between(self, start: datetime, end: datetime) -> Self:
        """Filter records whose block expires within a datetime range (inclusive).

        This method filters records that are blocked with a `blocked_until`
        timestamp between the start and end dates (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset of records with blocked_until between start and end.
        """
        return self.filter(blocked_until__gte=start, blocked_until__lte=end)

    # ========== Existence checks ==========

    def exists_blocked(self) -> bool:
        """Check if any currently blocked records exist.

        Returns:
            True if at least one record is currently blocked, False otherwise.
        """
        return self.blocked().exists()

    # ========== Count methods ==========

    def count_blocked(self) -> int:
        """Count the number of currently blocked records.

        Returns:
            The total count of records that are currently blocked.
        """
        return self.blocked().count()

    def count_not_blocked(self) -> int:
        """Count the number of currently not blocked records.

        Returns:
            The total count of records that are not currently blocked.
        """
        return self.not_blocked().count()
