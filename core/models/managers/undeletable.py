"""Undeletable model manager that prevents accidental record deletion.

This module defines a specialized manager class that extends BaseManager with
delete protection safeguards. The manager uses UndeletableQuerySet as its
default queryset class, which overrides the delete() method to raise an
exception, preventing accidental or unauthorized deletion operations.

This pattern is essential for protecting critical data that should never be
deleted, such as system configuration, audit logs, or core reference data.
"""

from typing import Generic, TypeVar

from core.models.managers.base import BaseManager
from core.models.managers.querysets.undeletable import UndeletableQuerySet


UndeletableQuerySetType = TypeVar(
    "UndeletableQuerySetType", bound="UndeletableQuerySet"
)


class UndeletableManager(
    BaseManager[UndeletableQuerySetType], Generic[UndeletableQuerySetType]
):
    """A manager that prevents deletion of records by default.

    This manager class implements a protective layer around delete operations,
    ensuring that records cannot be deleted unless explicitly allowed through
    alternative means. It uses UndeletableQuerySet as its default queryset
    class, which blocks delete() operations at the queryset level.

    Key features:
    - Blocks the default delete() method by raising OperationNotAllowedError
    - Maintains compatibility with all other queryset operations
    - Can be overridden or bypassed through custom queryset methods if needed
    - Provides clear error messaging explaining why deletion is prohibited

    This manager is particularly useful for:
    - System-critical tables that must never be deleted
    - Reference data that other systems depend on
    - Audit trail records that require legal compliance
    - Models where deletion should require explicit authorization

    Attributes:
        model: The Django model class this manager is bound to.
        _db: The database alias this manager uses.
        _queryset_class: The queryset class used for constructing queries.
        _hints: Additional hints for the queryset.
        _built_with: Internal tracking for construction.
    """

    def get_queryset(self):
        """Return a new QuerySet instance that blocks delete operations.

        Returns:
            A UndeletableQuerySet instance bound to this manager's model
            and database, with delete() operations blocked.
        """
        return UndeletableQuerySet(self.model, using=self._db)

    def delete(self):
        """Prevent deletion at the manager level.

        This method delegates to the queryset's delete() method, which
        raises an exception to prevent deletion. This provides a consistent
        blocking mechanism whether delete() is called on the manager or
        on the queryset.

        Returns:
            This method never returns normally.

        Raises:
            OperationNotAllowedError: Always raised when this method is called,
                with a message indicating that deletion is prohibited.
        """
        return self.get_queryset().delete()
