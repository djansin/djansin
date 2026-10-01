"""Trustable manager mixin providing trust-level query methods at the manager level.

This module defines a mixin that adds trust-level filtering capabilities to
model managers. It delegates to the underlying queryset's trust filtering methods
while providing convenient manager-level access to common trust queries.

The mixin is designed to work with models that have a `trust_level` field with
a TrustLevel enumeration (UNTRUSTED, REGULAR, TRUSTED, CORE). Common use cases
include user reputation systems, content moderation, or any domain requiring
graduated trust classifications.
"""

from typing import Generic, TypeVar

from core.models.managers.querysets import BaseQuerySet


BaseQuerySetType = TypeVar("BaseQuerySetType", bound="BaseQuerySet")


class TrustableManagerMixin(Generic[BaseQuerySetType]):
    """A manager mixin that adds trust-level filtering capabilities.

    This mixin provides manager-level methods for filtering records based on
    their trust level. It delegates to the queryset's filtering methods while
    maintaining the standard manager interface.

    The trust level hierarchy is expected to be ordered such that higher values
    indicate greater trust (e.g., UNTRUSTED=0, REGULAR=1, TRUSTED=2, CORE=3).

    The mixin provides:
    - Exact trust level filtering (untrusted, regular, trusted, core)
    - Range-based filtering (trust_below, highly_trusted)

    This mixin is designed to be used with Django Managers and should be
    combined with TrustableQuerySetMixin for complete query capabilities.

    Attributes:
        get_queryset: Must be provided by the manager class using this mixin.
            Returns the queryset instance to apply filters on.

        model: The model class using this manager. Must have a TrustLevel
            enumeration defined on it.

        trust_level: The IntegerField used to store trust levels.
            Expected to be defined on the model using this mixin.

        TrustLevel: An enumeration defining available trust levels.
            Expected to be defined on the model using this mixin.
    """

    def untrusted(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only untrusted records.

        Returns:
            A queryset containing only records with UNTRUSTED trust level.
        """
        return self.get_queryset().filter(trust_level=self.model.TrustLevel.UNTRUSTED)

    def regular(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only regular trust records.

        Returns:
            A queryset containing only records with REGULAR trust level.
        """
        return self.get_queryset().filter(trust_level=self.model.TrustLevel.REGULAR)

    def trusted(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only trusted records.

        Returns:
            A queryset containing only records with TRUSTED trust level.
        """
        return self.get_queryset().filter(trust_level=self.model.TrustLevel.TRUSTED)

    def core(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only core trust records.

        Returns:
            A queryset containing only records with CORE trust level.
        """
        return self.get_queryset().filter(trust_level=self.model.TrustLevel.CORE)

    def trust_below(self, level: int) -> BaseQuerySetType:
        """Return a queryset of records with trust level below TRUSTED.

        This method provides a convenient way to filter for low-trust records
        (UNTRUSTED and REGULAR).

        Args:
            level: The trust level threshold. This parameter is maintained
                for API consistency but the method always uses TRUSTED as
                the threshold.

        Returns:
            A queryset containing records with trust_level < TRUSTED.
        """
        return self.get_queryset().filter(trust_level__lt=self.model.TrustLevel.TRUSTED)

    def highly_trusted(self) -> BaseQuerySetType:
        """Return a queryset of records with high trust levels.

        Records with trust level at or above TRUSTED are considered highly
        trusted (TRUSTED and CORE).

        Returns:
            A queryset containing records with trust_level >= TRUSTED.
        """
        return self.get_queryset().filter(
            trust_level__gte=self.model.TrustLevel.TRUSTED
        )
