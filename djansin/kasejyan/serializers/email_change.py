"""Serializer definitions for the email-change code-request flow."""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.serializers import Serializer


class ChangeEmailSerializer(Serializer):
    """Serializer validating the payload for confirming an email change.

    Accepts the new email address and the six-digit verification code
    that was sent to it.

    Attributes:
        new_email (serializers.EmailField): Write-only new email address.
        code (serializers.CharField): Write-only six-digit verification
            code that was sent to ``new_email``.
    """

    new_email = serializers.EmailField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("New email is required."),
            "blank": _t("New email cannot be blank."),
            "null": _t("New email cannot be null."),
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


class RequestChangeEmailSerializer(Serializer):
    """Serializer validating the payload for requesting an email-change code.

    Accepts a single write-only ``new_email`` address. Field-level
    validation enforces presence and syntactic validity; the
    "not already owned" rule and code dispatch are handled by the
    service layer.

    Attributes:
        new_email (serializers.EmailField): Write-only email address
            that should replace the current one.
    """

    new_email = serializers.EmailField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("New email is required."),
            "blank": _t("New email cannot be blank."),
            "null": _t("New email cannot be null."),
            "invalid": _t("Enter a valid email address."),
        },
    )
