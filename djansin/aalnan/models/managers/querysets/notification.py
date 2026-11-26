"""QuerySet definitions for the ``aalnan`` app."""

from typing import Self

from core.models.managers.querysets import BaseQuerySet


class NotificationQuerySet(BaseQuerySet):
    """QuerySet for the :class:`~djansin.aalnan.models.Notification` model."""

    def for_user(self, user) -> Self:
        """Filter to notifications belonging to ``user``."""
        return self.filter(user=user)

    def unread(self) -> Self:
        """Filter to unread notifications."""
        return self.filter(is_read=False)

    def read(self) -> Self:
        """Filter to read notifications."""
        return self.filter(is_read=True)

    def newest_first(self) -> Self:
        """Order by ``created_at`` descending."""
        return self.order_by("-created_at")
