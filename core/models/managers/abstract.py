"""Abstract model manager implementation providing common CRUD and query utilities.

This module defines a generic abstract manager class that extends Django's
Manager with commonly used methods for retrieving, checking existence of,
and counting model instances. It uses the AbstractQuerySet as the default
query set class and provides convenience methods for single object
retrieval and aggregated counts.
"""

from typing import Generic, TypeVar

from django.db.models import Manager, Model

from core.models.managers.querysets.abstract import AbstractQuerySet


AbstractQuerySetType = TypeVar("AbstractQuerySetType", bound="AbstractQuerySet")


class AbstractManager(Manager, Generic[AbstractQuerySetType]):
    """An abstract model manager providing common retrieval and counting utilities.

    This manager extends Django's default Manager with methods for retrieving
    objects by ID, getting the latest or earliest records, checking existence,
    and performing common counts. It uses the AbstractQuerySet as its default
    queryset class and supports generic typing for the underlying model.

    Attributes:
        model: The Django model class this manager is bound to.
        _db: The database alias this manager uses.
        _queryset_class: The queryset class used for constructing queries.
        _hints: Additional hints for the queryset.
        _built_with: Internal tracking for construction.
    """

    def get_queryset(self) -> AbstractQuerySet:
        """Return a new QuerySet instance with the default queryset class.

        Returns:
            An AbstractQuerySet instance bound to this manager's model and database.
        """
        return AbstractQuerySet(self.model, using=self._db)

    # ========== Single Object Retrieval ==========

    def find_by_id(self, obj_id: int) -> Model | None:
        """Retrieve a single object by its primary key ID.

        Args:
            obj_id: The integer primary key value to look up.

        Returns:
            The model instance if found, None otherwise.
        """
        return self.get_queryset().by_id(obj_id).first()

    def find_latest(self) -> Model | None:
        """Retrieve the most recently created object.

        Returns:
            The latest model instance by created_at (descending), or None if no records exist.
        """
        return self.get_queryset().order_by_newest().first()

    def find_earliest(self) -> Model | None:
        """Retrieve the oldest created object.

        Returns:
            The earliest model instance by created_at (ascending), or None if no records exist.
        """
        return self.get_queryset().order_by_oldest().first()

    def find_latest_updated(self) -> Model | None:
        """Retrieve the most recently updated object.

        Returns:
            The latest model instance by updated_at (descending), or None if no records exist.
        """
        return self.get_queryset().order_by_newest_update().first()

    # ========== Existence Checks ==========

    def exists_by_id(self, obj_id: int) -> bool:
        """Check if an object with the given primary key ID exists.

        Args:
            obj_id: The integer primary key value to check.

        Returns:
            True if an object with the ID exists, False otherwise.
        """
        return self.get_queryset().exists_by_id(obj_id)

    # ========== Count Methods ==========

    def count_all(self) -> int:
        """Count all objects in the queryset.

        Returns:
            The total number of objects.
        """
        return self.get_queryset().count()

    def count_created_within_days(self, days: int) -> int:
        """Count objects created within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of objects created in the last `days` days.
        """
        return self.get_queryset().created_within_days(days).count()

    def count_created_today(self) -> int:
        """Count objects created today.

        Returns:
            The count of objects with created_at date equal to today.
        """
        return self.get_queryset().created_today().count()

    def count_updated_within_days(self, days: int) -> int:
        """Count objects updated within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of objects updated in the last `days` days.
        """
        return self.get_queryset().updated_within_days(days).count()

    def count_updated_today(self) -> int:
        """Count objects updated today.

        Returns:
            The count of objects with updated_at date equal to today.
        """
        return self.get_queryset().updated_today().count()
