"""Serializer definitions for the username-change flow.

This module exposes :class:`ChangeUsernameSerializer`, a DRF serializer
that validates the payload used by the username-change view. The payload
must contain a single ``new_username`` that satisfies the project's
identifier format rules.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidUsername
from core.serializers import Serializer
from core.utils.user_identifier import (
    collect_username_errors,
    is_valid_username,
)


class ChangeUsernameSerializer(Serializer):
    """Serializer validating the payload for changing a username.

    Accepts a single write-only ``new_username`` string. Field-level
    validation enforces presence and length; ``validate_new_username``
    enforces the identifier format rules (lowercase letters, digits,
    and ``.``, ``_``, ``-``), collecting per-rule errors into a single
    :class:`InvalidUsername` on failure.

    Uniqueness and the "must differ from the current username" rule are
    enforced by the service layer, where the user instance is available.

    Attributes:
        new_username (serializers.CharField): Write-only new username
            supplied by the client. Length must be between 5 and 255
            characters.
    """

    new_username = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        min_length=5,
        max_length=255,
        error_messages={
            "required": _t("New username is required."),
            "blank": _t("New username cannot be blank."),
            "null": _t("New username cannot be null."),
            "min_length": _t("New username must be at least 5 characters long."),
            "max_length": _t("New username cannot exceed 255 characters."),
        },
    )

    def validate_new_username(self, new_username: str) -> str:
        """Validate the raw ``new_username`` field value.

        Ensures the value satisfies the general identifier format rules
        (lowercase letters, digits, and ``.``, ``_``, ``-``) and, on
        failure, raises an :class:`InvalidUsername` populated with the
        collected per-rule errors.

        Args:
            new_username (str): The raw new username provided by the client.

        Returns:
            str: The validated new username, unchanged.

        Raises:
            InputError: If the new username does not conform to the
                expected format.
        """
        if not is_valid_username(username=new_username):
            errs = collect_username_errors(new_username)
            raise self.raise_input_error(
                InvalidUsername("\n".join(f"{e}" for e in errs))
            )

        return new_username
