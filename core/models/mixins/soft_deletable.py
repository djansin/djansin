"""Soft-deletable model mixin providing soft deletion capabilities.

This module defines an abstract model mixin that adds soft deletion functionality
to Django models. Soft deletion allows records to be logically deleted without
being physically removed from the database, preserving data history and enabling
recovery of deleted records.

The mixin provides a deleted_at timestamp field, properties for checking
deletion status, methods for soft-deleting and restoring records, and utilities
for analyzing deletion history. It also supports cascading soft deletes to
related objects through optional cascade methods.
"""

from datetime import datetime

from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions.common import BusinessError
from core.exceptions.errors.business import (
    ObjectAlreadyDeleted,
    ResourceNotSaved,
    UndeleteActiveObject,
)
from core.models.mixins.abstract import AbstractModelMixin


class SoftDeletableModelMixin(AbstractModelMixin):
    """An abstract model mixin that adds soft deletion capabilities.

    This mixin extends AbstractModelMixin with a deleted_at timestamp field
    and comprehensive soft deletion functionality. Records are considered
    active when deleted_at is None and soft-deleted when deleted_at contains
    a timestamp.

    Key features:
    - Automatic tracking of deletion time
    - Atomic soft-delete and restore operations
    - Support for cascading soft deletes to related objects
    - Deletion age calculation and retention policy checks
    - Time-based deletion history queries

    The mixin supports the following workflow:
    1. Soft-delete a record using soft_delete(), which sets deleted_at
    2. Check deletion status using is_deleted property
    3. Restore a deleted record using undelete(), which clears deleted_at
    4. Check if a record can be permanently deleted using can_be_permanently_deleted()

    For cascading soft deletes, implement soft_delete_cascade() and/or
    undelete_cascade() methods on your model.

    Attributes:
        deleted_at: A DateTimeField storing the timestamp when the record was
            soft-deleted. Null for active records.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Deleted at"),
        help_text=_t("Timestamp when the record was soft-deleted."),
    )

    class Meta:
        """Metadata configuration for SoftDeletableModelMixin.

        Makes this model abstract and adds a partial index for querying
        soft-deleted records efficiently.

        The partial index on deleted_at only includes records where
        deleted_at isn't None, making queries on deleted_at more efficient
        while saving storage space.
        """

        abstract = True

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft-deleted.

        Returns:
            True if the record is not active (deleted), False otherwise.
        """
        return self.deleted_at is not None

    @property
    def is_not_deleted(self) -> bool:
        """Check if the record is not soft-deleted.

        Returns:
            True if the record is active (not deleted), False otherwise.
        """
        return not self.is_deleted

    @property
    def deletion_age_in_days(self) -> int | None:
        """Get the age of deletion in days.

        Returns:
            The number of days since deletion, or None if the record
            is not soft-deleted.
        """
        if not self.is_deleted:
            return None
        delta = timezone.now() - self.deleted_at
        return delta.days

    @transaction.atomic
    def soft_delete(
        self, using: str = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Soft-delete the current record.

        This method marks the record as deleted by recording the current
        timestamp in deleted_at. It also updates the updated_at timestamp.
        The operation is performed atomically.

        If the model has a soft_delete_cascade method, it will be called
        to handle cascading soft deletes to related objects.

        Args:
            using: The database alias to use for the operation.
            keep_parents: If True, cascade delete rules for parent models
                are not followed (passed to cascade method if used).

        Returns:
            A tuple containing:
                - The total number of objects deleted (including cascades)
                - A dictionary mapping model labels to deletion counts

        Raises:
            BusinessError: If the instance is not saved (no primary key)
                or is already soft-deleted.
        """
        # Returns (0, {}) for unsaved instances to match Django's native delete() behavior.
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        now = timezone.now()
        total_count = self.__class__.objects.model._base_manager.filter(
            pk=self.pk, deleted_at__isnull=True
        ).update(deleted_at=now, updated_at=now)

        if total_count == 0:
            raise BusinessError(
                ObjectAlreadyDeleted(
                    model_name=_t("resource"), object_id=str(self.uuid)
                )
            )

        delete_result = {self._meta.label: total_count}

        cascade_result = getattr(self, "soft_delete_cascade", None)
        if cascade_result:
            count, result = cascade_result(using=using, keep_parents=keep_parents)
            total_count += count
            delete_result.update(result)

        return (total_count, delete_result)

    @transaction.atomic
    def undelete(
        self, using: str = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Restore a soft-deleted record.

        This method reactivates a soft-deleted record by clearing deleted_at.
        The updated_at timestamp is also updated to the current time.
        The operation is performed atomically.

        If the model has an undelete_cascade method, it will be called
        to handle cascading undeletion of related objects.

        Args:
            using: The database alias to use for the operation.
            keep_parents: If True, cascade delete rules for parent models
                are not followed (passed to cascade method if used).

        Returns:
            A tuple containing:
                - The total number of objects restored (including cascades)
                - A dictionary mapping model labels to restoration counts

        Raises:
            BusinessError: If the instance is not saved (no primary key)
                or is not currently soft-deleted.
        """
        # Returns (0, {}) for unsaved instances to match Django's native delete() behavior.
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        total_count = self.__class__.objects.model._base_manager.filter(
            pk=self.pk, deleted_at__isnull=False
        ).update(deleted_at=None, updated_at=timezone.now())

        if total_count == 0:
            raise BusinessError(
                UndeleteActiveObject(model_name=_t("object"), object_id=str(self.uuid))
            )

        undelete_result = {self._meta.label: total_count}

        cascade_result = getattr(self, "undelete_cascade", None)
        if cascade_result:
            count, result = cascade_result(using=using, keep_parents=keep_parents)
            total_count += count
            undelete_result.update(result)

        return (total_count, undelete_result)

    def was_deleted_before(self, timestamp: datetime) -> bool:
        """Check if the record was soft-deleted before a specific timestamp.

        Args:
            timestamp: The datetime threshold to check against.

        Returns:
            True if the record is deleted and its deleted_at is before the timestamp,
            False otherwise.
        """
        return self.is_deleted and self.deleted_at < timestamp

    def was_deleted_after(self, timestamp: datetime) -> bool:
        """Check if the record was soft-deleted after a specific timestamp.

        Args:
            timestamp: The datetime threshold to check against.

        Returns:
            True if the record is deleted and its deleted_at is after the timestamp,
            False otherwise.
        """
        return self.is_deleted and self.deleted_at > timestamp

    def was_deleted_today(self) -> bool:
        """Check if the record was soft-deleted today.

        Returns:
            True if the record is deleted and its deleted_at date is today,
            False otherwise.
        """
        if not self.is_deleted:
            return False
        return self.deleted_at.date() == timezone.now().date()

    def can_be_permanently_deleted(self, retention_days: int = 30) -> bool:
        """Check if the soft-deleted record is eligible for permanent deletion.

        This method determines if a soft-deleted record has exceeded the
        retention period and can be permanently removed from the database.

        Args:
            retention_days: The minimum number of days the record must remain
                soft-deleted before it can be permanently deleted. Defaults to 30.

        Returns:
            True if the record is soft-deleted and has been deleted for longer
            than the retention period, False otherwise.
        """
        if not self.is_deleted:
            return False
        delta = timezone.now() - self.deleted_at
        return delta.days > retention_days
