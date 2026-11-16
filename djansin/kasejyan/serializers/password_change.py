"""Serializer definitions for the password-change flow.

This module exposes :class:`ChangePasswordSerializer`, a DRF serializer
that validates the payload used by the password-change view. The payload
must contain the current password, the new password, and a matching
confirmation of the new password.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat
from core.serializers import Serializer


class ChangePasswordSerializer(Serializer):
    """Serializer validating the payload for changing a user's password.

    Accepts the current password (for re-authentication), the new
    password, and a matching confirmation of the new password. Field-level
    validation enforces presence and minimum length; object-level
    validation ensures the confirmation matches. Deeper password policy
    checks (similarity to user attributes, common-password lists, etc.)
    are delegated to the service layer, where the user instance is
    available.

    Attributes:
        current_password (serializers.CharField): Write-only current
            password, used to re-authenticate the user.
        new_password (serializers.CharField): Write-only new password.
            Minimum length is 8 characters.
        new_password_confirm (serializers.CharField): Write-only
            confirmation matching ``new_password``.
    """

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=False,
        error_messages={
            "required": _t("Current password is required."),
            "blank": _t("Current password cannot be blank."),
            "null": _t("Current password cannot be null."),
        },
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=False,
        min_length=8,
        error_messages={
            "required": _t("New password is required."),
            "blank": _t("New password cannot be blank."),
            "null": _t("New password cannot be null."),
            "min_length": _t("New password must be at least 8 characters long."),
        },
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=False,
        min_length=8,
        error_messages={
            "required": _t("New password confirmation is required."),
            "blank": _t("New password confirmation cannot be blank."),
            "null": _t("New password confirmation cannot be null."),
            "min_length": _t(
                "New password confirmation must be at least 8 characters long."
            ),
        },
    )

    def validate(self, data: dict) -> dict:
        """Perform object-level validation across the serializer fields.

        Enforces the following invariants:
            * ``new_password`` and ``new_password_confirm`` must match.
            * ``new_password`` must differ from ``current_password``.

        Args:
            data (dict): The validated field data collected by DRF.

        Returns:
            dict: The same ``data`` mapping, after all checks pass.

        Raises:
            InputError: If any of the invariants above is violated.
        """
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        new_password_confirm = data.get("new_password_confirm")

        if new_password != new_password_confirm:
            self.raise_input_error(
                InvalidFormat(expected_format=_t("matching new password confirmation"))
            )

        if new_password == current_password:
            self.raise_input_error(
                InvalidFormat(
                    expected_format=_t(
                        "a new password different from the current password"
                    )
                )
            )

        return data
