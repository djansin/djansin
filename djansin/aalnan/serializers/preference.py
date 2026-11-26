"""Serializers for the ``aalnan`` app.

Input serializers validate client payloads; output serializers are
used **only** for drf-spectacular schema generation — the views return
``to_dict()`` output directly.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.serializers import Serializer


# --- Input ---


class UpdateNotificationPreferenceSerializer(Serializer):
    """Payload for updating notification preferences."""

    in_app_enabled = serializers.BooleanField(required=False)
    email_enabled = serializers.BooleanField(required=False)
    sms_enabled = serializers.BooleanField(required=False)

    def validate(self, data: dict) -> dict:
        if not data:
            raise self.raise_input_error(
                serializers.ValidationError(
                    _t("At least one preference must be provided.")
                )
            )
        return data


# --- Output (for drf-spectacular) ---


class NotificationResultSerializer(Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField()
    data = serializers.JSONField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()
