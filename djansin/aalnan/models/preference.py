"""Model definitions for the ``aalnan`` app.

Defines :class:`Notification`, an in-app notification delivered to a
user, and :class:`NotificationPreference`, a per-user channel opt-in
record used by future email/SMS dispatch.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.models.base import Model


class NotificationPreference(Model):
    """Per-user opt-in for notification channels."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
        verbose_name=_t("User"),
    )
    in_app_enabled = models.BooleanField(
        default=True,
        verbose_name=_t("In-app enabled"),
    )
    email_enabled = models.BooleanField(
        default=False,
        verbose_name=_t("Email enabled"),
    )
    sms_enabled = models.BooleanField(
        default=False,
        verbose_name=_t("SMS enabled"),
    )

    class Meta:
        verbose_name = _t("Notification preference")
        verbose_name_plural = _t("Notification preferences")

    def __str__(self) -> str:
        return f"Preferences for {self.user.username}"
