"""Serializer definitions for the account-deactivation flow.

This module exposes :class:`DeactivateAccountSerializer`, a DRF
serializer that validates the payload used by the account-deactivation
view. The payload must contain the current password for
re-authentication, and may optionally include a reason for auditing.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.serializers import Serializer


class DeactivateAccountSerializer(Serializer):
    """Serializer validating the payload for deactivating an account.

    Accepts the user's current password for re-authentication — the same
    safeguard used by password changes, protecting against an attacker
    who has gained temporary access to an unlocked device. An optional
    ``reason`` may be supplied for audit purposes.

    Attributes:
        current_password (serializers.CharField): Write-only current
            password, used to re-authenticate the user.
        reason (serializers.CharField | None): Optional free-text reason
            for deactivation. Capped at 500 characters.
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
    reason = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
        max_length=500,
        trim_whitespace=True,
        error_messages={
            "max_length": _t("Reason cannot exceed 500 characters."),
        },
    )


class AccountDeactivationResultSerializer(Serializer):
    """Payload of a successful account deactivation."""

    username = serializers.CharField()
    deactivated_at = serializers.DateTimeField()
    revoked_sessions = serializers.ListField(
        child=serializers.DictField(),
        help_text=(
            "Each entry contains ``jti``, ``username``, ``created_at``, "
            "``expires_at``, and ``revoked_at``."
        ),
    )


class AccountDeactivationEnvelopeSerializer(Serializer):
    """Envelope for ``DeactivateAccountView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = AccountDeactivationResultSerializer()
