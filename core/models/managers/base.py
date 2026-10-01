"""Concrete model manager implementation extending the abstract manager with UUID-based retrieval.

This module defines a base manager class that extends AbstractManager with additional
methods for retrieving and checking objects by UUID. It uses BaseQuerySet as its
default queryset class, providing both the abstract query utilities (ID-based and
time-based filtering) and UUID-specific query methods.

The manager is generic and can be used with any model that has a 'uuid' field.
"""

from typing import Generic, TypeVar

from django.db.models import Model

from core.models.managers.abstract import AbstractManager
from core.models.managers.querysets.base import BaseQuerySet


BaseQuerySetType = TypeVar("BaseQuerySetType", bound="BaseQuerySet")


class BaseManager(AbstractManager[BaseQuerySetType], Generic[BaseQuerySetType]):
    """An extended model manager providing UUID-based retrieval capabilities.

    This manager builds upon AbstractManager by adding methods specifically
    for retrieving objects by UUID. It uses BaseQuerySet as the default
    queryset class, which inherits all abstract query utilities and adds
    UUID-based filtering methods.

    Inherited from AbstractManager:
    - ID-based retrieval: find_by_id()
    - Latest/earliest retrieval: find_latest(), get_earliest(), find_latest_updated()
    - Existence checks: exists_by_id()
    - Counting methods: count_all(), count_created_within_days(), etc.

    Added by this manager:
    - UUID-based retrieval: find_by_uuid()
    - UUID-based existence check: exists_by_uuid()

    Attributes:
        model: The Django model class this manager is bound to.
        _db: The database alias this manager uses.
        _queryset_class: The queryset class used for constructing queries.
            Overridden to use BaseQuerySet instead of AbstractQuerySet.
    """

    def get_queryset(self) -> BaseQuerySet:
        """Return a new QuerySet instance with the default queryset class.

        Returns:
            A BaseQuerySet instance bound to this manager's model and database.
        """
        return BaseQuerySet(self.model, using=self._db)

    # ========== Single Object Retrieval ==========

    def find_by_uuid(self, uuid: str) -> Model | None:
        """Retrieve a single object by its UUID.

        Args:
            uuid: The UUID string to look up.

        Returns:
            The model instance if found, None otherwise.
        """
        return self.get_queryset().by_uuid(uuid).first()

    # ========== Existence Checks ==========

    def exists_by_uuid(self, uuid: str) -> bool:
        """Check if an object with the given UUID exists.

        Args:
            uuid: The UUID string to check.

        Returns:
            True if an object with the UUID exists, False otherwise.
        """
        return self.get_queryset().exists_by_uuid(uuid)
