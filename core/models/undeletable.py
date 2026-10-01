"""Undeletable base model that prevents accidental record deletion.

This module defines an abstract model that extends BaseModel with delete
protection safeguards. The model inherits timestamp fields, UUID identifier,
and custom manager from BaseModel, and adds protection against accidental
deletion by overriding the delete() method to raise an exception.

The model is designed for critical data that should never be deleted, such as
system configuration, audit logs, or core reference data. It provides an
explicit hard_delete() method for cases where deletion is intentionally required.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.exceptions.business import OperationNotAllowedError
from core.models.base import BaseModel
from core.models.managers.undeletable import UndeletableManager


class UndeletableModel(BaseModel):
    """A base model that prevents deletion of records by default.

    This abstract model extends BaseModel with delete protection, ensuring
    that records cannot be accidentally or unintentionally deleted. It is
    ideal for models that store critical or reference data that must be
    preserved.

    Features inherited from BaseModel:
    - Automatic timestamp tracking (created_at, updated_at)
    - Public UUID identifier for external references
    - Custom BaseManager with common query utilities

    Features added by UndeletableModel:
    - Protected delete() method that raises OperationNotAllowedError
    - Explicit hard_delete() method for intentional deletion
    - Optimized database index on created_at for time-based queries

    The model uses UndeletableManager, which blocks delete operations at both
    the manager and queryset levels, providing comprehensive protection.

    The model is abstract, serving as a template for concrete models rather
    than creating its own database table.

    Attributes:
        objects: The custom UndeletableManager instance bound to this model,
            providing delete protection at the manager level.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.

        uuid: UUIDField inherited from BaseModelMixin.
            Public immutable identifier for external references.
    """

    objects: UndeletableManager = UndeletableManager()

    class Meta:
        """Metadata configuration for UndeletableModel.

        Makes this model abstract so it doesn't create a database table,
        but provides fields to all inheriting models.

        An index on created_at (descending order) is provided to optimize
        time-based queries and reporting operations, particularly for
        retrieving the most recent records.

        This index is especially important for undeletable models that
        often serve as audit logs or reference data where chronological
        queries are common.
        """

        abstract = True

        indexes = [
            models.Index(
                fields=["-created_at"],
                name="%(app_label)s_%(class)s_time_idx",
            ),
        ]

    def delete(self, *args, **kwds):
        """Prevent deletion of this model instance.

        This method overrides the default delete() to raise an exception,
        ensuring that instances of this model cannot be deleted unless
        explicitly allowed through the hard_delete() method.

        The method is designed to fail fast and provide a clear error
        message explaining why deletion is not allowed, helping developers
        understand the need to use hard_delete() instead when deletion is
        genuinely required.

        Args:
            *args: Variable length argument list.
            **kwds: Arbitrary keyword arguments.

        Raises:
            OperationNotAllowedError: Always raised when this method is called,
                with a message indicating that this record cannot be deleted.
        """
        raise OperationNotAllowedError(reason_=_t("This record cannot be deleted."))

    def hard_delete(self, *args, **kwds):
        """Permanently delete this model instance.

        This method provides an explicit way to delete an instance when
        such operation is intentionally desired. It calls the parent
        class's delete() method, bypassing the protection implemented in
        the overridden delete() method.

        This should be used with caution and only when absolutely necessary.
        Consider whether archiving or soft deletion would be more appropriate
        for the use case before calling this method.

        Args:
            *args: Variable length argument list passed to the parent delete method.
            **kwds: Arbitrary keyword arguments passed to the parent delete method.
        """
        super().delete(*args, **kwds)
