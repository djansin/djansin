"""Soft-deletable base model combining soft deletion with core model features.

This module defines an abstract model that extends BaseModel with soft deletion
capabilities. The model inherits timestamp fields, UUID identifier, and custom
manager from BaseModel, and adds the deleted_at field and soft deletion methods
from SoftDeletableModelMixin.

The model includes specialized database indexes optimized for common soft-delete
query patterns, such as retrieving active records and filtering deleted records
by time ranges.
"""

from django.db import models

from core.models.base import BaseModel
from core.models.managers.soft_deletable import SoftDeletableManager
from core.models.mixins.soft_deletable import SoftDeletableModelMixin


class SoftDeletableModel(SoftDeletableModelMixin, BaseModel):
    """A comprehensive base model with soft deletion capabilities.

    This abstract model combines the core features of BaseModel with soft
    deletion functionality from SoftDeletableModelMixin, providing a complete
    foundation for models that require logical deletion.

    Features inherited from BaseModel:
    - Automatic timestamp tracking (created_at, updated_at)
    - Public UUID identifier for external references
    - Custom BaseManager with common query utilities

    Features added by SoftDeletableModelMixin:
    - Soft deletion with deleted_at timestamp
    - Soft-delete and restore operations with cascade support
    - Deletion status properties and time-based queries
    - Retention policy checking

    The model uses SoftDeletableManager, which automatically filters out
    soft-deleted records from default queries while providing explicit methods
    to work with deleted records.

    The model is abstract, serving as a template for concrete models rather
    than creating its own database table.

    Attributes:
        objects: The custom SoftDeletableManager instance bound to this model,
            providing soft-delete-specific methods like deleted(), not_deleted(),
            purge_deleted(), and other query utilities.

        deleted_at: DateTimeField inherited from SoftDeletableModelMixin.
            Stores the timestamp when the record was soft-deleted.
            Null for active records.

        uuid: UUIDField inherited from BaseModelMixin.
            Public immutable identifier for external references.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    objects: SoftDeletableManager = SoftDeletableManager()

    class Meta:
        """Metadata configuration for SoftDeletableModel.

        Makes this model abstract and adds specialized partial indexes
        to optimize common soft-delete query patterns.

        The indexes are designed to improve performance for the most
        frequent queries:
        - Listing active (non-deleted) records ordered by creation date
        - Filtering soft-deleted records by deletion time
        - Aggregating and counting deleted records by time ranges

        The partial indexes use conditions to index only relevant records,
        saving storage space and improving query performance by reducing
        index size.

        Indexes:
            - deleted_at_idx: Partial index on deleted_at for records with
              deleted_at IS NOT NULL, optimizing queries on deleted records
            - no_deleted_idx: Partial index on -created_at for records with
              deleted_at IS NULL, optimizing queries on active records
        """

        abstract = True

        indexes = [
            # Optimize queries that look for deleted records within time range
            models.Index(
                fields=["deleted_at"],
                condition=models.Q(deleted_at__isnull=False),
                name="%(app_label)s_%(class)s_deleted_at_idx",
            ),
            # Optimize queries that filter non-deleted records
            models.Index(
                fields=["-created_at"],
                condition=models.Q(deleted_at__isnull=True),
                name="%(app_label)s_%(class)s_no_deleted_idx",
            ),
        ]
