"""Serializer definitions for the authentication sign-in/sign-up flow.

Exposes :class:`AuthenticateSerializer`, a DRF serializer that validates
the payload used by the authentication view to either log in an existing
user or register a new one. The payload must contain an ``identifier``
together with exactly one of: a password (plus matching confirmation) or
a one-time verification code.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat, InvalidUsername
from core.serializers import Serializer
from core.utils.user_identifier import (
    collect_username_errors,
    is_valid_email,
    is_valid_identifier,
    is_valid_phone,
)
from djansin.kasejyan.serializers.user import UserSerializer


class AuthenticateSerializer(Serializer):
    """Serializer validating credentials for authentication or registration.

    Accepts a single ``identifier`` (email, phone number, or username)
    and exactly one credential path: either a ``password`` with a
    matching ``password_confirm``, or a six-digit ``code`` for
    contact-based verification.

    Field-level validation enforces presence, length, and format.
    Object-level validation enforces mutual exclusivity (password XOR
    code), password confirmation matching, and — when using the code
    path — that the identifier is a contact (email or phone), not a
    username.

    Attributes:
        identifier (serializers.CharField): Write-only identifier
            supplied by the client. Length must be between 5 and 255
            characters.
        password (serializers.CharField | None): Write-only password,
            when using the password-based path. Minimum length is 8
            characters. Optional; defaults to ``None``.
        password_confirm (serializers.CharField | None): Write-only
            confirmation matching ``password``. Optional; defaults to
            ``None``.
        code (serializers.CharField | None): Write-only six-digit
            verification code, when using the code-based path. Optional;
            defaults to ``None``.
    """

    identifier = serializers.CharField(
        write_only=True,
        required=True,
        min_length=5,
        max_length=255,
        error_messages={
            "required": _t("Identifier is required."),
            "blank": _t("Identifier cannot be blank."),
            "min_length": _t("Identifier must be at least 5 characters long."),
            "max_length": _t("Identifier cannot exceed 255 characters."),
        },
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        allow_null=True,
        default=None,
        min_length=8,
        error_messages={
            "blank": _t("Password cannot be blank."),
            "min_length": _t("Password must be at least 8 characters long."),
        },
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        allow_null=True,
        default=None,
        min_length=8,
        error_messages={
            "blank": _t("Password confirmation cannot be blank."),
            "min_length": _t(
                "Password confirmation must be at least 8 characters long."
            ),
        },
    )
    code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        allow_null=True,
        default=None,
        min_length=6,
        max_length=6,
        error_messages={
            "blank": _t("Verification code cannot be blank."),
            "min_length": _t("Verification code must be exactly 6 characters long."),
            "max_length": _t("Verification code must be exactly 6 characters long."),
        },
    )

    def validate_identifier(self, identifier: str) -> str:
        """Validate the raw ``identifier`` field value.

        Ensures the value satisfies the general identifier format rules
        (lowercase letters, digits, and ``.``, ``_``, ``-``) and, on
        failure, raises an :class:`InvalidUsername` populated with the
        collected per-rule errors.

        Args:
            identifier (str): The raw identifier provided by the client.

        Returns:
            str: The validated identifier, unchanged.

        Raises:
            InputError: If the identifier does not conform to the
                expected format.
        """
        if not is_valid_identifier(identifier=identifier):
            errors = collect_username_errors(identifier)
            raise self.raise_input_error(InvalidUsername(field_errors=errors))

        return identifier

    def validate(self, data: dict) -> dict:
        """Perform object-level validation across the serializer fields.

        Enforces the following invariants:

        * Exactly one credential path is provided: either ``password``
          or ``code``, but not both.
        * When ``password`` is provided, ``password_confirm`` must be
          present and match it.
        * When ``code`` is provided, the ``identifier`` must resolve to
          a valid email address or phone number (not a username), since
          verification codes are only dispatched to contacts.

        Args:
            data (dict): The validated field data collected by DRF.

        Returns:
            dict: The same ``data`` mapping, after all checks pass.

        Raises:
            InputError: If any of the invariants above are violated.
        """
        identifier = data.get("identifier")
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        verification_code = data.get("code")

        has_password = bool(password)
        has_code = bool(verification_code)

        if (has_password and has_code) or not (has_password or has_code):
            self.raise_input_error(
                InvalidFormat(
                    expected_format=_t(
                        "either a password or a verification code, not both"
                    )
                )
            )

        if not has_password:
            if not (is_valid_phone(identifier) or is_valid_email(identifier)):
                self.raise_input_error(
                    InvalidFormat(
                        expected_format=_t(
                            "a valid phone number, email address, not a username"
                        )
                    )
                )
        elif password != password_confirm:
            self.raise_input_error(
                InvalidFormat(expected_format=_t("matching password confirmation"))
            )

        return data


class EnvelopeSerializer(Serializer):
    """Standard response envelope used by every auth endpoint."""

    message = serializers.CharField(help_text="Human-readable result message.")
    code = serializers.CharField(help_text="Machine-readable result code.")
    data = serializers.JSONField(help_text="Endpoint-specific payload.")


class TokenPairSerializer(Serializer):
    """Token pair and its metadata, as returned by IssueTokenResult."""

    token_type = serializers.CharField(default="Bearer")
    refresh = serializers.CharField()
    access = serializers.CharField()
    access_expires_at = serializers.DateTimeField()
    refresh_expires_at = serializers.DateTimeField()
    access_expires_in = serializers.IntegerField()
    refresh_expires_in = serializers.IntegerField()
    user = UserSerializer()


class AuthTokenEnvelopeSerializer(EnvelopeSerializer):
    """Envelope for ``AuthenticateView`` and ``RefreshTokenView``."""

    data = TokenPairSerializer()
