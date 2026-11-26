"""Model definitions for the ``aalnan`` app.

Defines :class:`Notification`, an in-app notification delivered to a
user, and :class:`NotificationPreference`, a per-user channel opt-in
record used by future email/SMS dispatch.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.models.base import Model
from djansin.aalnan.models.enums import NotificationType
from djansin.aalnan.models.managers.notification import NotificationManager


class Notification(Model):
    """An in-app notification delivered to a single user."""

    objects: NotificationManager = NotificationManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_t("User"),
        help_text=_t("The user this notification belongs to."),
    )
    type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        db_index=True,
        verbose_name=_t("Type"),
        help_text=_t("The kind of event this notification describes."),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_t("Title"),
        help_text=_t("Short, human-readable title."),
    )
    body = models.TextField(
        verbose_name=_t("Body"),
        help_text=_t("Full notification text."),
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_t("Data"),
        help_text=_t("Structured payload for client-side rendering."),
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_t("Is read"),
        help_text=_t("Whether the user has marked this as read."),
    )

    class Meta:
        verbose_name = _t("Notification")
        verbose_name_plural = _t("Notifications")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.get_type_display()}] {self.title}"

    def mark_read(self, *, save: bool = True) -> None:
        """Mark this notification as read."""
        if self.is_read:
            return
        self.is_read = True
        if save:
            self.save(update_fields=["is_read", "updated_at"])
