"""Manager definitions for the ``aalnan`` app."""

from typing import TYPE_CHECKING

from core.models.managers import BaseManager
from djansin.aalnan.models.managers.querysets.notification import NotificationQuerySet


if TYPE_CHECKING:
    from djansin.aalnan.models import Notification


class NotificationManager(BaseManager[NotificationQuerySet]):
    """Manager for the :class:`~djansin.aalnan.models.Notification` model."""

    def get_queryset(self) -> NotificationQuerySet:
        return NotificationQuerySet(self.model, using=self._db)

    def for_user(self, user) -> NotificationQuerySet:
        return self.get_queryset().for_user(user)

    def unread_for_user(self, user) -> NotificationQuerySet:
        return self.for_user(user).unread()
