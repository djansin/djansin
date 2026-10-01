"""Abstract query set implementation providing common filtering and ordering utilities.

This module defines a base query set class that extends Django's QuerySet with
commonly used methods for ID-based filtering, time-based queries (using
created_at and updated_at timestamps), ordering, and existence checks.
These utilities serve as a foundation for concrete query set implementations
across the application.
"""

from datetime import datetime
from typing import Self

from django.db import models
from django.utils import timezone


class AbstractQuerySet(models.QuerySet):
    """An extended Django QuerySet providing common query utilities.

    This abstract query set adds methods for filtering by ID, querying by
    creation/update timestamps, ordering results by recency, and checking
    object existence. It is designed to be subclassed by concrete query
    sets that inherit these reusable behaviors.

    Attributes:
        model: The Django model class this query set is bound to.
        query: The underlying SQL query object.
        _result_cache: Cached results from the database.
        _sticky_filter: Internal flag for filter stickiness.
    """

    # ========== ID-based ==========

    def by_id(self, obj_id: int) -> Self:
        """Filter the queryset by a single primary key ID.

        Args:
            obj_id: The integer primary key value to filter by.

        Returns:
            A filtered queryset containing only the object with the given ID.
        """
        return self.filter(id=obj_id)

    def by_ids(self, obj_ids: list[int]) -> Self:
        """Filter the queryset by a list of primary key IDs.

        Args:
            obj_ids: A list of integer primary key values to filter by.

        Returns:
            A filtered queryset containing objects with IDs in the given list.
        """
        return self.filter(id__in=obj_ids)

    # ========== Time-based (created_at) ==========

    def created_before(self, timestamp: datetime) -> Self:
        """Filter objects created before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Objects created before this time
                will be included.

        Returns:
            A filtered queryset of objects with created_at < timestamp.
        """
        return self.filter(created_at__lt=timestamp)

    def created_after(self, timestamp: datetime) -> Self:
        """Filter objects created after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Objects created after this time
                will be included.

        Returns:
            A filtered queryset of objects with created_at > timestamp.
        """
        return self.filter(created_at__gt=timestamp)

    def created_between(self, start: datetime, end: datetime) -> Self:
        """Filter objects created within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset of objects with created_at between start and end.
        """
        return self.filter(created_at__gte=start, created_at__lte=end)

    def created_within_days(self, days: int) -> Self:
        """Filter objects created within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset of objects created in the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

    def created_today(self) -> Self:
        """Filter objects created today (based on the current date).

        Returns:
            A filtered queryset of objects where created_at date equals today.
        """
        today = timezone.now().date()
        return self.filter(created_at__date=today)

    # ========== Time-based (updated_at) ==========

    def updated_before(self, timestamp: datetime) -> Self:
        """Filter objects updated before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Objects updated before this time
                will be included.

        Returns:
            A filtered queryset of objects with updated_at < timestamp.
        """
        return self.filter(updated_at__lt=timestamp)

    def updated_after(self, timestamp: datetime) -> Self:
        """Filter objects updated after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Objects updated after this time
                will be included.

        Returns:
            A filtered queryset of objects with updated_at > timestamp.
        """
        return self.filter(updated_at__gt=timestamp)

    def updated_within_days(self, days: int) -> Self:
        """Filter objects updated within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset of objects updated in the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(updated_at__gte=cutoff)

    def updated_today(self) -> Self:
        """Filter objects updated today (based on the current date).

        Returns:
            A filtered queryset of objects where updated_at date equals today.
        """
        today = timezone.now().date()
        return self.filter(updated_at__date=today)

    # ========== Ordering ==========

    def order_by_newest(self) -> Self:
        """Order the queryset by creation date in descending order.

        Returns:
            A queryset ordered by created_at descending (newest first).
        """
        return self.order_by("-created_at")

    def order_by_oldest(self) -> Self:
        """Order the queryset by creation date in ascending order.

        Returns:
            A queryset ordered by created_at ascending (oldest first).
        """
        return self.order_by("created_at")

    def order_by_newest_update(self) -> Self:
        """Order the queryset by last update date in descending order.

        Returns:
            A queryset ordered by updated_at descending (most recently updated first).
        """
        return self.order_by("-updated_at")

    def order_by_oldest_update(self) -> Self:
        """Order the queryset by last update date in ascending order.

        Returns:
            A queryset ordered by updated_at ascending (least recently updated first).
        """
        return self.order_by("updated_at")

    # ========== Existence ==========

    def exists_by_id(self, obj_id: int) -> bool:
        """Check if an object with the given primary key ID exists.

        Args:
            obj_id: The integer primary key value to check.

        Returns:
            True if an object with the ID exists, False otherwise.
        """
        return self.filter(id=obj_id).exists()
