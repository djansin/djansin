"""Blockable model mixin providing temporary blocking capabilities.

This module defines an abstract model mixin that adds temporary blocking
functionality to Django models. The mixin allows records to be blocked for
a specified duration, preventing certain operations or access during the
block period.

The mixin is typically used for security features such as rate limiting,
failed login attempt tracking, or temporarily suspending access to resources
after repeated violations.
"""

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions.common import BusinessError
from core.exceptions.errors.business import (
    ResourceAlreadyBlocked,
    ResourceAlreadyUnblocked,
    ResourceNotSaved,
)
from core.models.mixins.abstract import AbstractModelMixin


class BlockableMixin(AbstractModelMixin):
    """An abstract model mixin that adds temporary blocking capabilities.

    This mixin extends AbstractModelMixin with a `blocked_until` timestamp
    field and methods for blocking and unblocking records. A record is
    considered blocked if `blocked_until` is in the future.

    Key features:
    - Automatic timestamp tracking (created_at, updated_at) from AbstractModelMixin
    - Block status checking via `is_blocked` property
    - Block operation with configurable duration
    - Unblock operation to clear the block
    - Validation to prevent redundant operations

    Typical use cases:
    - Rate limiting after failed login attempts
    - Temporarily locking resources during maintenance
    - Suspending user accounts for security violations
    - Preventing duplicate submissions in a time window

    Attributes:
        blocked_until: A nullable DateTimeField storing when the block expires.
            Null means the record is not blocked. If set, the record is
            blocked until the specified timestamp.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    blocked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Blocked Until"),
        help_text=_t(
            "Temporarily blocked until this time due to failed attempts or security policies."
        ),
    )

    class Meta:
        """Metadata configuration for BlockableMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides blocking fields to all inheriting models.
        """

        abstract = True

    @property
    def is_blocked(self) -> bool:
        """Check if the record is currently blocked.

        A record is considered blocked if `blocked_until` is set and the
        current time is before the block expiration.

        Returns:
            True if the record is currently blocked, False otherwise.
        """
        return self.blocked_until is not None and timezone.now() < self.blocked_until

    def block(self, duration_minutes: int = 30) -> None:
        """Block the record for a specified duration.

        This method sets the `blocked_until` timestamp to the current time
        plus the specified duration. It prevents duplicate blocking by only
        updating records that are not currently blocked.

        Args:
            duration_minutes: The number of minutes to block the record.
                Defaults to 30 minutes.

        Raises:
            BusinessError: If the record is not saved (no primary key) or
                is already blocked.
        """
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        blocked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(
                Q(blocked_until__isnull=True) | Q(blocked_until__lte=timezone.now())
            )
            .update(blocked_until=blocked_until, updated_at=timezone.now())
        )

        if updated_count == 0:
            raise BusinessError(ResourceAlreadyBlocked())

    def unblock(self) -> None:
        """Unblock the record.

        This method clears the `blocked_until` timestamp, effectively
        unblocking the record. It only updates records that are currently
        blocked, preventing unnecessary operations on already unblocked records.

        Raises:
            BusinessError: If the record is not saved (no primary key) or
                is not currently blocked.
        """
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        updated_count = (
            self.__class__.objects.model._base_manager.filter(pk=self.pk)
            .filter(blocked_until__isnull=False, blocked_until__gte=timezone.now())
            .update(blocked_until=None, updated_at=timezone.now())
        )

        if updated_count == 0:
            raise BusinessError(ResourceAlreadyUnblocked())
