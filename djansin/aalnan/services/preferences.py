"""Service layer for reading and updating notification preferences."""

from core.services import Service
from djansin.aalnan.models import NotificationPreference
from djansin.aalnan.types import NotificationPreferenceResult
from djansin.kasejyan.models import User


class GetNotificationPreferenceService(Service[NotificationPreferenceResult]):
    """Return the user's notification preferences, creating defaults."""

    def execute(self, *, user: User) -> NotificationPreferenceResult:
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        return self._to_result(prefs)

    @staticmethod
    def _to_result(prefs: NotificationPreference) -> NotificationPreferenceResult:
        return NotificationPreferenceResult(
            in_app_enabled=prefs.in_app_enabled,
            email_enabled=prefs.email_enabled,
            sms_enabled=prefs.sms_enabled,
        )


class UpdateNotificationPreferenceService(Service[NotificationPreferenceResult]):
    """Update the user's notification preferences."""

    def execute(
        self,
        *,
        user: User,
        in_app_enabled: bool | None = None,
        email_enabled: bool | None = None,
        sms_enabled: bool | None = None,
    ) -> NotificationPreferenceResult:
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)

        update_fields = ["updated_at"]
        if in_app_enabled is not None:
            prefs.in_app_enabled = in_app_enabled
            update_fields.append("in_app_enabled")
        if email_enabled is not None:
            prefs.email_enabled = email_enabled
            update_fields.append("email_enabled")
        if sms_enabled is not None:
            prefs.sms_enabled = sms_enabled
            update_fields.append("sms_enabled")

        prefs.save(update_fields=update_fields)

        return NotificationPreferenceResult(
            in_app_enabled=prefs.in_app_enabled,
            email_enabled=prefs.email_enabled,
            sms_enabled=prefs.sms_enabled,
        )
