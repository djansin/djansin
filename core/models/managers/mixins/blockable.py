"""Blockable manager mixin providing block-related query methods at the manager level.

This module defines a mixin that adds block-related filtering capabilities to
model managers. It delegates to the underlying queryset's block filtering methods
while providing convenient manager-level access to common block queries.

The mixin is designed to work with models that have a `blocked_until` timestamp
field, where a record is considered blocked if `blocked_until` is in the future.
"""

from typing import Generic, TypeVar

from django.db.models import Q
from django.utils import timezone

from core.models.managers.querysets import BaseQuerySet


BaseQuerySetType = TypeVar("BaseQuerySetType", bound="BaseQuerySet")


class BlockableManagerMixin(Generic[BaseQuerySetType]):
    """A manager mixin that adds block-related filtering capabilities.

    This mixin provides manager-level methods for filtering records based on
    their block status. It delegates to the queryset's filtering methods while
    maintaining the standard manager interface.

    A record is considered:
    - Blocked: If `blocked_until` is in the future (blocked_until > now)
    - Not blocked: If `blocked_until` is null or in the past (blocked_until <= now)

    The mixin provides:
    - Status-based filtering (blocked, not_blocked)
    - Counting methods (count_blocked)
    - Existence checks (exists_blocked)

    This mixin is designed to be used with Django Managers and should be
    combined with BlockableQuerySetMixin for complete query capabilities.

    Attributes:
        get_queryset: Must be provided by the manager class using this mixin.
            Returns the queryset instance to apply filters on.
    """

    # ========== Delegation to queryset ==========

    def blocked(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only currently blocked records.

        A record is considered blocked if its `blocked_until` timestamp is
        in the future relative to the current time.

        Returns:
            A filtered queryset containing records with blocked_until > now.
        """
        return self.get_queryset().filter(blocked_until__gt=timezone.now())

    def not_blocked(self) -> BaseQuerySetType:
        """Return a queryset filtered to exclude currently blocked records.

        A record is considered not blocked if its `blocked_until` timestamp
        is null or in the past relative to the current time.

        Returns:
            A filtered queryset containing records that are not currently
            blocked (blocked_until is null or <= now).
        """
        return self.get_queryset().filter(
            Q(blocked_until__isnull=True) | Q(blocked_until__lte=timezone.now())
        )

    # ========== Count methods ==========

    def count_blocked(self) -> int:
        """Count the number of currently blocked records.

        Returns:
            The total count of records that are currently blocked.
        """
        return self.blocked().count()

    # ========== Existence checks ==========

    def exists_blocked(self) -> bool:
        """Check if any currently blocked records exist.

        Returns:
            True if at least one record is currently blocked, False otherwise.
        """
        return self.blocked().exists()
