"""Serializer definitions for the email-removal flow.

This module exposes :class:`RemoveEmailSerializer`, a DRF serializer
that validates the payload used by the email-removal view. The payload
must contain the email address to remove and the one-time verification
code that was sent to it.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.serializers import Serializer


class RemoveEmailSerializer(Serializer):
    """Serializer validating the payload for removing an email address.

    Accepts the email address to detach from the authenticated user's
    account, together with the six-digit verification code that was
    dispatched to that address. Field-level validation enforces presence
    and format; ownership, the "last login method" guard, and code
    validity are enforced by the service layer.

    Attributes:
        email (serializers.EmailField): Write-only email address to
            remove. Must be a syntactically valid email.
        code (serializers.CharField): Write-only six-digit verification
            code that was sent to ``email``.
    """

    email = serializers.EmailField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("Email is required."),
            "blank": _t("Email cannot be blank."),
            "null": _t("Email cannot be null."),
            "invalid": _t("Enter a valid email address."),
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


class RequestRemoveEmailSerializer(Serializer):
    """Serializer validating the payload for requesting an email-removal code.

    Accepts a single write-only ``email`` address. Field-level
    validation enforces presence and syntactic validity; ownership, the
    "last login method" guard, and the "no still-valid code" rule are
    enforced by the service layer.

    Attributes:
        email (serializers.EmailField): Write-only email address whose
            removal is being requested. Must be a syntactically valid
            email.
    """

    email = serializers.EmailField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("Email is required."),
            "blank": _t("Email cannot be blank."),
            "null": _t("Email cannot be null."),
            "invalid": _t("Enter a valid email address."),
        },
    )
