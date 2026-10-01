"""Concrete query set implementation extending the abstract query set with UUID-based filtering.

This module defines a base query set class that extends AbstractQuerySet with
additional methods for filtering by UUID fields. It provides convenience methods
for querying objects by single or multiple UUIDs, as well as checking existence
by UUID. This query set is designed to be used with models that use UUID as
a primary or secondary identifier field.
"""

from typing import Self

from core.models.managers.querysets.abstract import AbstractQuerySet


class BaseQuerySet(AbstractQuerySet):
    """An extended query set providing UUID-based filtering capabilities.

    This query set builds upon AbstractQuerySet by adding methods specifically
    for filtering objects by UUID fields. It assumes the model has a 'uuid'
    field that can be used for filtering. All methods in this query set return
    a new queryset instance, maintaining the chainable nature of Django's
    QuerySet API.

    This class inherits all ID-based and time-based filtering methods from
    AbstractQuerySet, including by_id(), created_between(), order_by_newest(),
    and exists_by_id().

    Attributes:
        model: The Django model class this query set is bound to.
        query: The underlying SQL query object.
        _result_cache: Cached results from the database.
        _sticky_filter: Internal flag for filter stickiness.
    """

    # ========== UUID-based ==========

    def by_uuid(self, uuid: str) -> Self:
        """Filter the queryset by a single UUID string.

        Args:
            uuid: The UUID string to filter by.

        Returns:
            A filtered queryset containing only the object with the given UUID.
        """
        return self.filter(uuid=uuid)

    def by_uuids(self, uuids: list[str]) -> Self:
        """Filter the queryset by a list of UUID strings.

        Args:
            uuids: A list of UUID strings to filter by.

        Returns:
            A filtered queryset containing objects with UUIDs in the given list.
        """
        return self.filter(uuid__in=uuids)

    # ========== Existence ==========

    def exists_by_uuid(self, uuid: str) -> bool:
        """Check if an object with the given UUID exists.

        Args:
            uuid: The UUID string to check.

        Returns:
            True if an object with the UUID exists, False otherwise.
        """
        return self.filter(uuid=uuid).exists()
