"""Soft-deletable query set implementation providing soft deletion utilities.

This module defines a query set class that extends BaseQuerySet with soft
deletion functionality. Soft deletion allows records to be logically deleted
without being physically removed from the database, preserving data history
and enabling recovery of deleted records.

The query set provides methods to filter out deleted records, restore them,
and manage soft-deletion states across query operations.
"""

from typing import Self

from django.utils import timezone

from core.models.managers.querysets.base import BaseQuerySet


class SoftDeletableQuerySet(BaseQuerySet):
    """An extended query set that adds soft deletion capabilities.

    This query set builds upon BaseQuerySet and provides methods for working
    with soft-deleted records. Soft deletion is implemented using a nullable
    deleted_at timestamp field: when a record is deleted, the deleted_at
    field is set to the current timestamp; when restored, it is set to null.

    The class is designed to be used with models that include a deleted_at
    field, typically through a soft-deletable mixin. It provides convenient
    methods for filtering out deleted records and bulk restoring records.

    Attributes:
        model: The Django model class this query set is bound to.
        query: The underlying SQL query object.
        _result_cache: Cached results from the database.
        _sticky_filter: Internal flag for filter stickiness.
    """

    def not_deleted(self) -> Self:
        """Filter the queryset to include only non-deleted records.

        This method excludes all records that have been soft-deleted by
        filtering out those with a non-null deleted_at value. The resulting
        queryset contains only active, non-deleted records.

        Returns:
            A filtered queryset containing only records where deleted_at is null.
        """
        return self.filter(deleted_at__isnull=True)

    def soft_delete(
        self, using: str = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Soft-delete all records in the queryset.

        This method performs a bulk soft deletion by setting the deleted_at
        and updated_at timestamps to the current time for all records in the
        queryset. The records are not physically removed from the database.

        Args:
            using: The database alias to use for the operation.
                This parameter is maintained for API consistency with Django's
                native delete() method.
            keep_parents: If True, cascade delete rules for parent models
                are not followed. This parameter is maintained for API
                consistency with Django's native delete() method.

        Returns:
            A tuple containing:
                - The total number of records soft-deleted
                - A dictionary mapping model labels to deletion counts
        """
        now = timezone.now()
        total_count = self.update(deleted_at=now, updated_at=now)

        return (total_count, {self.model._meta.label: total_count})

    def undelete(self) -> tuple[int, dict[str, int]]:
        """Restore all soft-deleted records in the queryset.

        This method performs a bulk restore by clearing the deleted_at field
        and updating the updated_at timestamp to the current time for all
        records in the queryset. The records become active again.

        Returns:
            A tuple containing:
                - The total number of records restored
                - A dictionary mapping model labels to restoration counts
        """
        total_count = self.update(deleted_at=None, updated_at=timezone.now())

        return (total_count, {self.model._meta.label: total_count})
