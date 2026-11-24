"""Output serializers for drf-spectacular documentation.

These serializers describe the response shape of the session-list
endpoint. They are **not** used at runtime — the view returns
``to_dict()`` output directly. Their sole purpose is to give
drf-spectacular enough metadata to render accurate documentation.
"""

from rest_framework import serializers

from core.serializers import Serializer


class UserSessionResultSerializer(Serializer):
    """A single active session in the list."""

    jti = serializers.CharField()
    username = serializers.CharField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()


class UserSessionsEnvelopeSerializer(Serializer):
    """Envelope for ``ListUserSessionsView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = UserSessionResultSerializer(many=True)
