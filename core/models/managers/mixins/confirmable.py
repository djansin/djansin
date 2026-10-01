"""Confirmable manager mixin providing confirmation-related query methods at the manager level.

This module defines a mixin that adds confirmation-related filtering capabilities to
model managers. It delegates to the underlying queryset's confirmation filtering methods
while providing convenient manager-level access to common confirmation queries.

The mixin is designed to work with models that have `confirmed_at` and `created_at`
timestamp fields, commonly used for email verification, OTP validation, or any workflow
requiring user confirmation.
"""

from typing import Generic, TypeVar

from django.utils import timezone

from core.models.managers.querysets import BaseQuerySet


BaseQuerySetType = TypeVar("BaseQuerySetType", bound="BaseQuerySet")


class ConfirmableManagerMixin(Generic[BaseQuerySetType]):
    """A manager mixin that adds confirmation-related filtering capabilities.

    This mixin provides manager-level methods for filtering records based on
    their confirmation status. It delegates to the queryset's filtering methods
    while maintaining the standard manager interface.

    The mixin provides:
    - Status-based filtering (confirmed, unconfirmed)
    - Cleanup utilities (ready_for_cleanup)
    - Counting methods (count_confirmed)
    - Existence checks (exists_confirmed)

    This mixin is designed to be used with Django Managers and should be
    combined with ConfirmableQuerySetMixin for complete query capabilities.

    Attributes:
        get_queryset: Must be provided by the manager class using this mixin.
            Returns the queryset instance to apply filters on.

        confirmed_at: The DateTimeField used to determine confirmation status.
            Expected to be defined on the model using this mixin.

        created_at: The DateTimeField used for age-based cleanup queries.
            Expected to be defined on the model using this mixin.
    """

    # ========== Delegation to queryset ==========

    def confirmed(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only confirmed records.

        Returns:
            A filtered queryset containing only records where confirmed_at is not None.
        """
        return self.get_queryset().filter(confirmed_at__isnull=False)

    def unconfirmed(self) -> BaseQuerySetType:
        """Return a queryset filtered to include only unconfirmed records.

        Returns:
            A filtered queryset containing only records where confirmed_at is None.
        """
        return self.get_queryset().filter(confirmed_at__isnull=True)

    def ready_for_cleanup(self, confirmation_expiry_days: int = 30) -> BaseQuerySetType:
        """Return unconfirmed records ready for cleanup.

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

    # ========== Count methods ==========

    def count_confirmed(self) -> int:
        """Count confirmed records.

        Returns:
            The total count of records where confirmed_at is not None.
        """
        return self.confirmed().count()

    # ========== Existence checks ==========

    def exists_confirmed(self) -> bool:
        """Check if any confirmed records exist.

        Returns:
            True if at least one confirmed record exists, False otherwise.
        """
        return self.confirmed().exists()
