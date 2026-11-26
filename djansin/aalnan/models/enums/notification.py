"""Enumerations for the ``aalnan`` app.

Defines the notification types that services may emit. New types
should be added here so clients can rely on a stable, documented set
of values.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _t


class NotificationType(models.TextChoices):
    """The kind of event a notification describes."""

    LOGIN = "login", _t("Successful login")
    PASSWORD_CHANGED = "password_changed", _t("Password changed")
    EMAIL_CHANGED = "email_changed", _t("Email changed")
    PHONE_CHANGED = "phone_changed", _t("Phone changed")
    EMAIL_REMOVED = "email_removed", _t("Email removed")
    PHONE_REMOVED = "phone_removed", _t("Phone removed")
    SESSION_REVOKED = "session_revoked", _t("Session revoked")
    ALL_SESSIONS_REVOKED = "all_sessions_revoked", _t("All sessions revoked")
    ACCOUNT_DEACTIVATED = "account_deactivated", _t("Account deactivated")
