"""Output serializers for drf-spectacular documentation.

These serializers describe the response shape of the session-revoke
endpoint. They are **not** used at runtime — the view returns
``to_dict()`` output directly. Their sole purpose is to give
drf-spectacular enough metadata to render accurate documentation.
"""

from rest_framework import serializers

from core.serializers import Serializer


class RevokedSessionResultSerializer(Serializer):
    """Payload of a successful session revocation."""

    jti = serializers.CharField()
    username = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    revoked_at = serializers.DateTimeField()


class RevokedSessionEnvelopeSerializer(Serializer):
    """Envelope for ``RevokeSessionView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = RevokedSessionResultSerializer()
