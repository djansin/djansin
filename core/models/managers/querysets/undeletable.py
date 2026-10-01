"""Undeletable query set implementation that prevents accidental record deletion.

This module defines a query set class that extends BaseQuerySet with safeguards
against accidental or unauthorized deletion operations. The class overrides
the default delete() method to raise an exception, while providing an explicit
hard_delete() method for cases where deletion is intentionally required.

This pattern is useful for protecting critical data, enforcing business rules,
or implementing audit trails where deletion should be restricted or require
special authorization.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions.business import OperationNotAllowedError
from core.models.managers.querysets.base import BaseQuerySet


class UndeletableQuerySet(BaseQuerySet):
    """A query set that prevents deletion of records by default.

    This query set class implements a protective layer around the delete()
    operation, raising an exception when deletion is attempted. This is
    particularly useful for:

    - Protecting critical system records that should never be deleted
    - Enforcing business rules that prohibit deletion of certain entities
    - Preventing accidental data loss through bulk delete operations
    - Implementing authorization checks where deletion requires special
      permissions

    The class provides two methods for deletion:
    - delete(): Protected version that always raises OperationNotAllowedError
    - hard_delete(): Explicit bypass method that performs actual deletion

    This design forces developers to explicitly choose hard_delete() when
    deletion is genuinely intended, making accidental deletions less likely.

    Attributes:
        model: The Django model class this query set is bound to.
        query: The underlying SQL query object.
        _result_cache: Cached results from the database.
        _sticky_filter: Internal flag for filter stickiness.
    """

    def delete(self) -> tuple[int, dict[str, int]]:
        """Prevent deletion of records from this queryset.

        This method overrides the default delete() to raise an exception,
        ensuring that records in this queryset cannot be deleted unless
        explicitly allowed through the hard_delete() method.

        The method is designed to fail fast and provide a clear error
        message explaining why the operation is not allowed, helping
        developers understand the need to use hard_delete() instead.

        Returns:
            This method never returns normally.

        Raises:
            OperationNotAllowedError: Always raised when this method is called,
                with a message indicating that deletion is prohibited.
        """
        raise OperationNotAllowedError(
            reason=_t("Deleting records from this collection is strictly prohibited.")
        )

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Permanently delete records from this queryset.

        This method provides an explicit way to delete records when such
        operation is intentionally desired. It calls the parent class's
        delete() method, bypassing the protection implemented in the
        overridden delete() method.

        This should be used with caution and only when absolutely necessary.
        Consider whether soft deletion or archiving would be more appropriate
        for the use case before calling this method.

        Returns:
            A tuple containing the number of deleted objects and a dictionary
            of the number of deletions per object type, in Django's standard
            delete() return format.
        """
        return super().delete()
