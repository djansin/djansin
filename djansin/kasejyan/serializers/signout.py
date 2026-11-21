"""Serializer for the sign-out flow.

Exposes :class:`SignoutSerializer`, a DRF serializer that validates the
payload used by the sign-out view. The payload must contain either a
``refresh`` token (to revoke the current session) or ``all_devices=true``
(to revoke every session of the authenticated user).
"""

from rest_framework import serializers

from core.exceptions.errors.validation import RequiredField
from core.serializers import Serializer


class SignoutSerializer(Serializer):
    """Serializer validating the payload for signing out.

    Accepts an optional ``refresh`` token and an optional ``all_devices``
    flag. Exactly one path must be selected:

    * ``all_devices=True`` — revoke every session of the authenticated
      user, regardless of which session issued the request.
    * ``all_devices=False`` (default) with a non-blank ``refresh`` —
      revoke only the session the token belongs to.

    If neither condition holds, object-level validation raises a
    :class:`RequiredField` error for ``refresh``.

    Attributes:
        refresh (serializers.CharField): Write-only refresh token
            identifying the session to revoke. Optional; required only
            when ``all_devices`` is ``False``.
        all_devices (serializers.BooleanField): When ``True``, revoke
            every session of the authenticated user. Defaults to
            ``False``.
    """

    refresh = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
    )
    all_devices = serializers.BooleanField(default=False)

    def validate(self, attrs: dict) -> dict:
        """Perform object-level validation across the serializer fields.

        Enforces the following invariant:

        * If ``all_devices`` is ``False``, a non-blank ``refresh`` token
          must be provided.

        Args:
            attrs (dict): The validated field data collected by DRF.

        Returns:
            dict: The same ``attrs`` mapping, after the check passes.

        Raises:
            InputError: If ``all_devices`` is ``False`` and no non-blank
                ``refresh`` token was supplied.
        """
        if not attrs.get("all_devices") and not attrs.get("refresh"):
            self.raise_input_error(RequiredField(field="'refresh'"))
        return attrs
