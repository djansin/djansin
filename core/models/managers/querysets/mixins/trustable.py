"""Trustable query set mixin providing filtering and query utilities for trustable models.

This module defines a mixin that adds trust-level filtering capabilities to
query sets. It provides methods for filtering records based on trust levels,
which are typically used for user reputation systems, content moderation, or
any domain requiring graduated trust classifications.

The mixin is designed to work with models that have a `trust_level` field,
typically an IntegerField with predefined choices representing different
trust categories (UNTRUSTED, REGULAR, TRUSTED, CORE).
"""

from typing import Self


class TrustableQuerySetMixin:
    """A mixin that adds trust-level filtering capabilities to query sets.

    This mixin provides a comprehensive set of methods for querying records
    based on their trust level. It assumes the model has a `trust_level`
    field with an associated `TrustLevel` enumeration or choices class.

    The mixin provides:
    - Exact trust level filtering (trust_level, untrusted, regular, trusted, core)
    - Range-based filtering (trust_above, trust_below, trust_between)
    - Combined filters (highly_trusted, low_trust)
    - Ordering utilities (order_by_trust)

    The trust level hierarchy is expected to be ordered such that higher values
    indicate greater trust (e.g., UNTRUSTED=0, REGULAR=1, TRUSTED=2, CORE=3).

    This mixin is designed to be used with Django QuerySets and can be combined
    with other query set mixins for comprehensive query capabilities.

    Attributes:
        trust_level: The IntegerField used to store trust levels.
            Expected to be defined on the model using this mixin.

        TrustLevel: An enumeration or choices class defining available trust levels.
            Expected to be defined on the model using this mixin.
    """

    def trust_level(self, level: int) -> Self:
        """Filter the queryset by a specific trust level.

        Args:
            level: The trust level value to filter by (exact match).

        Returns:
            A filtered queryset containing records with the specified
            trust level.
        """
        return self.filter(trust_level=level)

    def untrusted(self) -> Self:
        """Filter the queryset to include only untrusted records.

        Returns:
            A filtered queryset containing records with UNTRUSTED trust level.
        """
        return self.filter(trust_level=self.model.TrustLevel.UNTRUSTED)

    def regular(self) -> Self:
        """Filter the queryset to include only regular trust records.

        Returns:
            A filtered queryset containing records with REGULAR trust level.
        """
        return self.filter(trust_level=self.model.TrustLevel.REGULAR)

    def trusted(self) -> Self:
        """Filter the queryset to include only trusted records.

        Returns:
            A filtered queryset containing records with TRUSTED trust level.
        """
        return self.filter(trust_level=self.model.TrustLevel.TRUSTED)

    def core(self) -> Self:
        """Filter the queryset to include only core trust records.

        Returns:
            A filtered queryset containing records with CORE trust level.
        """
        return self.filter(trust_level=self.model.TrustLevel.CORE)

    def trust_above(self, level: int) -> Self:
        """Filter records with trust level above a specified value.

        Args:
            level: The trust level threshold. Records with trust_level
                greater than this value will be included.

        Returns:
            A filtered queryset with trust_level > level.
        """
        return self.filter(trust_level__gt=level)

    def trust_below(self, level: int) -> Self:
        """Filter records with trust level below a specified value.

        Args:
            level: The trust level threshold. Records with trust_level
                less than this value will be included.

        Returns:
            A filtered queryset with trust_level < level.
        """
        return self.filter(trust_level__lt=level)

    def trust_between(self, min_level: int, max_level: int) -> Self:
        """Filter records with trust level within a range (inclusive).

        Args:
            min_level: The minimum trust level (inclusive).
            max_level: The maximum trust level (inclusive).

        Returns:
            A filtered queryset with trust_level between min_level and max_level.
        """
        return self.filter(trust_level__gte=min_level, trust_level__lte=max_level)

    def highly_trusted(self) -> Self:
        """Filter records with high trust levels.

        Records with trust level at or above TRUSTED are considered highly trusted.

        Returns:
            A filtered queryset containing records with trust_level >= TRUSTED.
        """
        return self.filter(trust_level__gte=self.model.TrustLevel.TRUSTED)

    def low_trust(self) -> Self:
        """Filter records with low trust levels.

        Records with trust level below TRUSTED are considered low trust.

        Returns:
            A filtered queryset containing records with trust_level < TRUSTED.
        """
        return self.filter(trust_level__lt=self.model.TrustLevel.TRUSTED)

    def order_by_trust(self, descending: bool = True) -> Self:
        """Order records by trust level.

        Args:
            descending: If True, order highest trust first. Defaults to True.

        Returns:
            An ordered queryset by trust_level.
        """
        order = "-trust_level" if descending else "trust_level"
        return self.order_by(order)
