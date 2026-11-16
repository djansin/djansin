"""Serializer definitions for the password-reset flow.

This module exposes two DRF serializers used by the password-reset
endpoints:

* :class:`RequestPasswordResetSerializer` — validates the identifier
  used to request a verification code.
* :class:`PasswordResetSerializer` — validates the identifier,
  the verification code, and the new password (with confirmation).
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat
from core.serializers import Serializer


class RequestPasswordResetSerializer(Serializer):
    """Serializer validating the payload for requesting a password reset.

    Accepts a single ``identifier`` (email, phone number, or username).
    The service layer resolves the user, picks the preferred contact
    channel, and dispatches a verification code.

    Attributes:
        identifier (serializers.CharField): Write-only identifier
            supplied by the client. Length must be between 5 and 255
            characters.
    """

    identifier = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        min_length=5,
        max_length=255,
        error_messages={
            "required": _t("Identifier is required."),
            "blank": _t("Identifier cannot be blank."),
            "null": _t("Identifier cannot be null."),
            "min_length": _t("Identifier must be at least 5 characters long."),
            "max_length": _t("Identifier cannot exceed 255 characters."),
        },
    )


class PasswordResetSerializer(Serializer):
    """Serializer validating the payload for confirming a password reset.

    Accepts the ``identifier`` that received the code, the six-digit
    ``code`` itself, and the ``new_password`` together with a matching
    confirmation. Field-level validation enforces presence, length, and
    code format; object-level validation ensures the confirmation
    matches and the new password differs from the code (a common
    copy-paste mistake). Deeper password-policy checks (similarity to
    user attributes, common-password lists, etc.) are delegated to the
    service layer, where the user instance is available.

    Attributes:
        identifier (serializers.CharField): Write-only identifier that
            received the verification code.
        code (serializers.CharField): Write-only six-digit verification
            code.
        new_password (serializers.CharField): Write-only new password.
            Minimum length is 8 characters.
        new_password_confirm (serializers.CharField): Write-only
            confirmation matching ``new_password``.
    """

    identifier = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        min_length=5,
        max_length=255,
        error_messages={
            "required": _t("Identifier is required."),
            "blank": _t("Identifier cannot be blank."),
            "null": _t("Identifier cannot be null."),
            "min_length": _t("Identifier must be at least 5 characters long."),
            "max_length": _t("Identifier cannot exceed 255 characters."),
        },
    )
    code = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        min_length=6,
        max_length=6,
        error_messages={
            "required": _t("Verification code is required."),
            "blank": _t("Verification code cannot be blank."),
            "null": _t("Verification code cannot be null."),
            "min_length": _t("Verification code must be exactly 6 characters long."),
            "max_length": _t("Verification code must be exactly 6 characters long."),
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
            * ``new_password`` must not equal the verification ``code``
              (a common copy-paste mistake that would otherwise produce
              a trivially guessable password).

        Args:
            data (dict): The validated field data collected by DRF.

        Returns:
            dict: The same ``data`` mapping, after all checks pass.

        Raises:
            InputError: If any of the invariants above is violated.
        """
        new_password = data.get("new_password")
        new_password_confirm = data.get("new_password_confirm")
        code = data.get("code")

        if new_password != new_password_confirm:
            self.raise_input_error(
                InvalidFormat(expected_format=_t("matching new password confirmation"))
            )

        if new_password == code:
            self.raise_input_error(
                InvalidFormat(
                    expected_format=_t(
                        "a new password different from the verification code"
                    )
                )
            )

        return data
