"""Soft-deletable model manager providing comprehensive soft deletion utilities.

This module defines a specialized manager class that extends BaseManager with
comprehensive soft deletion capabilities. The manager automatically excludes
soft-deleted records from default queries while providing explicit methods to
work with deleted records, filter by deletion time, count records, and purge
(deleted permanently) soft-deleted records.

Soft deletion is implemented using a nullable deleted_at timestamp field:
- Records with deleted_at=None are considered active/non-deleted
- Records with deleted_at set are considered soft-deleted
"""

from datetime import datetime
from typing import Generic, TypeVar

from django.utils import timezone

from core.models.managers.base import BaseManager
from core.models.managers.querysets.soft_deletable import SoftDeletableQuerySet


SoftDeletableQuerySetType = TypeVar(
    "SoftDeletableQuerySetType", bound="SoftDeletableQuerySet"
)


class SoftDeletableManager(
    BaseManager[SoftDeletableQuerySetType], Generic[SoftDeletableQuerySetType]
):
    """A manager for models that support soft deletion.

    This manager automatically excludes soft-deleted records (deleted_at is
    not null) from all default queries, ensuring that most database operations
    work only with active records. It provides explicit methods to include,
    filter, count, and permanently delete soft-deleted records.

    The manager extends BaseManager and uses SoftDeletableQuerySet as its
    queryset class. It provides a comprehensive API for managing soft-deleted
    records including:

    - Automatic filtering of deleted records from default queries
    - Methods to include or specifically target deleted records
    - Time-based filtering of deletion timestamps
    - Counting methods for deleted and active records
    - Purge operations for permanently removing old soft-deleted records

    Attributes:
        model: The Django model class this manager is bound to.
        _db: The database alias this manager uses.
        _queryset_class: The queryset class used for constructing queries.
        _hints: Additional hints for the queryset.
        _built_with: Internal tracking for construction.
    """

    def get_queryset(self) -> SoftDeletableQuerySet:
        """Return a new QuerySet that automatically excludes soft-deleted records.

        Returns:
            A SoftDeletableQuerySet instance filtered to only include
            non-deleted records (where deleted_at is None).
        """
        return SoftDeletableQuerySet(self.model, using=self._db).not_deleted()

    def include_deleted(self) -> SoftDeletableQuerySetType:
        """Return a queryset that includes all records, including soft-deleted ones.

        This method provides access to the complete queryset without the
        default soft-delete filter, allowing operations on deleted records.

        Returns:
            A queryset containing all records, both deleted and non-deleted.
        """
        return self.get_queryset().model._base_manager

    # ========== Core filtering (delegation to queryset) ==========

    def deleted(self) -> SoftDeletableQuerySetType:
        """Return a queryset filtered to include only soft-deleted records.

        Returns:
            A queryset containing only records where deleted_at isn't None.
        """
        return self.include_deleted().filter(deleted_at__isnull=False)

    def not_deleted(self) -> SoftDeletableQuerySetType:
        """Return a queryset filtered to include only non-deleted records.

        This is the default queryset, explicitly exposed for clarity.

        Returns:
            A queryset containing only records where deleted_at is None.
        """
        return self.get_queryset()

    # ========== Time-based deletion filtering ==========

    def deleted_before(self, timestamp: datetime) -> SoftDeletableQuerySetType:
        """Filter soft-deleted records that were deleted before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Deleted records with deleted_at
                before this time will be included.

        Returns:
            A queryset of soft-deleted records with deleted_at < timestamp.
        """
        return self.deleted().filter(deleted_at__lt=timestamp)

    def deleted_after(self, timestamp: datetime) -> SoftDeletableQuerySetType:
        """Filter soft-deleted records that were deleted after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Deleted records with deleted_at
                after this time will be included.

        Returns:
            A queryset of soft-deleted records with deleted_at > timestamp.
        """
        return self.deleted().filter(deleted_at__gt=timestamp)

    def deleted_between(
        self, start: datetime, end: datetime
    ) -> SoftDeletableQuerySetType:
        """Filter soft-deleted records within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A queryset of soft-deleted records with deleted_at between start and end.
        """
        return self.deleted().filter(deleted_at__gte=start, deleted_at__lte=end)

    def deleted_today(self) -> SoftDeletableQuerySetType:
        """Filter soft-deleted records that were deleted today.

        Returns:
            A queryset of soft-deleted records with deleted_at date equal to today.
        """
        today = timezone.now().date()
        return self.deleted().filter(deleted_at__date=today)

    def deleted_within_days(self, days: int) -> SoftDeletableQuerySetType:
        """Filter soft-deleted records deleted within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A queryset of soft-deleted records with deleted_at in the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.deleted().filter(deleted_at__gte=cutoff)

    # ========== Count methods ==========

    def count_deleted(self) -> int:
        """Count the number of soft-deleted records.

        Returns:
            The total count of records where deleted_at isn't None.
        """
        return self.deleted().count()

    def count_deleted_before(self, timestamp: datetime) -> int:
        """Count soft-deleted records deleted before a specific timestamp.

        Args:
            timestamp: The datetime threshold.

        Returns:
            The count of soft-deleted records with deleted_at < timestamp.
        """
        return self.deleted_before(timestamp).count()

    def count_deleted_after(self, timestamp: datetime) -> int:
        """Count soft-deleted records deleted after a specific timestamp.

        Args:
            timestamp: The datetime threshold.

        Returns:
            The count of soft-deleted records with deleted_at > timestamp.
        """
        return self.deleted_after(timestamp).count()

    def count_deleted_between(self, start: datetime, end: datetime) -> int:
        """Count soft-deleted records within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            The count of soft-deleted records with deleted_at between start and end.
        """
        return self.deleted_between(start, end).count()

    def count_deleted_today(self) -> int:
        """Count soft-deleted records deleted today.

        Returns:
            The count of soft-deleted records with deleted_at date equal to today.
        """
        return self.deleted_today().count()

    def count_deleted_within_days(self, days: int) -> int:
        """Count soft-deleted records deleted within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of soft-deleted records with deleted_at in the last `days` days.
        """
        return self.deleted_within_days(days).count()

    def count_not_deleted(self) -> int:
        """Count the number of non-deleted (active) records.

        Returns:
            The total count of records where deleted_at is None.
        """
        return self.not_deleted().count()

    # ========== Existence checks ==========

    def exists_deleted(self) -> bool:
        """Check if any soft-deleted records exist.

        Returns:
            True if at least one soft-deleted record exists, False otherwise.
        """
        return self.deleted().exists()

    def exists_not_deleted(self) -> bool:
        """Check if any non-deleted records exist.

        Returns:
            True if at least one non-deleted record exists, False otherwise.
        """
        return self.not_deleted().exists()

    # ========== Purge operations (hard delete soft-deleted records) ==========

    def purge_deleted(self) -> tuple[int, dict[str, int]]:
        """Permanently delete all soft-deleted records.

        This performs a hard delete (remove from database) on all records
        where deleted_at isn't None. This operation cannot be undone.

        Returns:
            A tuple containing the number of deleted objects and a dictionary
            of the number of deletions per object type, in Django's standard
            delete() return format.
        """
        return self.deleted().delete()

    def purge_older_than(self, days: int) -> tuple[int, dict[str, int]]:
        """Permanently delete soft-deleted records older than N days.

        This performs a hard delete on soft-deleted records where deleted_at
        is older than the specified number of days.

        Args:
            days: The age threshold in days. Records soft-deleted more than
                `days` days ago will be permanently deleted.

        Returns:
            A tuple containing the number of deleted objects and a dictionary
            of the number of deletions per object type, in Django's standard
            delete() return format.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.deleted_before(cutoff).delete()

    def purge_deleted_before(self, timestamp: datetime) -> tuple[int, dict[str, int]]:
        """Permanently delete soft-deleted records deleted before a timestamp.

        This performs a hard delete on soft-deleted records with deleted_at
        before the specified timestamp.

        Args:
            timestamp: The datetime threshold. Records soft-deleted before
                this time will be permanently deleted.

        Returns:
            A tuple containing the number of deleted objects and a dictionary
            of the number of deletions per object type, in Django's standard
            delete() return format.
        """
        return self.deleted_before(timestamp).delete()
