"""Serializers for the ``aalnan`` app."""

from rest_framework import serializers

from core.serializers import Serializer


class NotificationListEnvelopeSerializer(Serializer):
    message = serializers.CharField()
    code = serializers.CharField()
    data = serializers.DictField(
        help_text="Contains ``count``, ``unread_count``, and ``results``."
    )


class NotificationPreferenceEnvelopeSerializer(Serializer):
    message = serializers.CharField()
    code = serializers.CharField()
    data = serializers.DictField(
        help_text="Contains ``in_app_enabled``, ``email_enabled``, ``sms_enabled``."
    )
