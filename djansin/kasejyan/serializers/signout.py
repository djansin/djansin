from rest_framework import serializers

from core.exceptions.errors.validation import RequiredField
from core.serializers import Serializer


class SignoutSerializer(Serializer):
    """Validate logout payload.

    ``refresh`` is required for revoking the current session. ``all_devices``
    optionally switches to revoking every session of the authenticated user.
    """

    refresh = serializers.CharField(required=False, allow_blank=False)
    all_devices = serializers.BooleanField(default=False)

    def validate(self, attrs: dict) -> dict:
        if not attrs.get("all_devices") and not attrs.get("refresh"):
            self.raise_input_error(RequiredField(field="'refresh'"))
        return attrs
