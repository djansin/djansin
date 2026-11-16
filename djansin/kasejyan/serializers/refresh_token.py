"""Serializer definitions for the refresh-token flow.

This module exposes :class:`RefreshTokenSerializer`, a DRF serializer that
validates the payload used by the token-refresh view. The payload must
contain exactly one non-blank ``refresh_token`` string.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat
from core.serializers import Serializer


class RefreshTokenSerializer(Serializer):
    """Serializer validating the payload for refreshing an access token.

    Accepts a single write-only ``refresh_token`` string. The value is a
    JWT issued previously by the authentication flow. Structural validation
    (presence, non-blank, minimum length) happens at the field level; the
    token's cryptographic validity and business rules (active user, not
    revoked, etc.) are enforced by :class:`RefreshTokenService`.

    Attributes:
        refresh_token (serializers.CharField): Write-only refresh token
            supplied by the client. Must be non-blank and at least 16
            characters long.
    """

    refresh_token = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=16,
        max_length=4096,
        error_messages={
            "required": _t("Refresh token is required."),
            "blank": _t("Refresh token cannot be blank."),
            "null": _t("Refresh token cannot be null."),
            "min_length": _t("Refresh token is too short to be valid."),
            "max_length": _t("Refresh token is too long to be valid."),
        },
    )

    def validate_refresh_token(self, refresh_token: str) -> str:
        """Validate the raw ``refresh_token`` field value.

        Performs a lightweight structural check to reject obviously
        malformed tokens before hitting the service layer (which would
        otherwise attempt to decode them). A JWT is composed of three
        dot-separated Base64URL segments; anything that doesn't match
        this shape cannot be a valid token and is rejected early.

        Args:
            refresh_token (str): The raw refresh token provided by the client.

        Returns:
            str: The validated refresh token, unchanged.

        Raises:
            InputError: If the token does not have the expected JWT shape.
        """
        if refresh_token.count(".") != 2 or any(
            not part for part in refresh_token.split(".")
        ):
            raise self.raise_input_error(
                InvalidFormat(expected_format=_t("a valid JWT refresh token"))
            )

        return refresh_token
