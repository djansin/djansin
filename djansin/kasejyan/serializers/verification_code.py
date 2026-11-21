"""Serializer for requesting a verification code.

Exposes :class:`VerificationCodeSerializer`, a DRF serializer that
validates the payload used to request a one-time verification code for
a contact identifier. Only valid email addresses and phone numbers are
accepted as identifiers.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.serializers import Serializer
from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.exceptions import InvalidIdentifier


class VerificationCodeSerializer(Serializer):
    """Serializer validating the identifier for a verification code request.

    Accepts a single ``identifier`` field and ensures it resolves to a
    valid email address or phone number. Usernames and any other formats
    are rejected with an
    :class:`~djansin.kasejyan.exceptions.InvalidIdentifier` error.

    Attributes:
        identifier (serializers.CharField): Write-only identifier
            supplied by the client. Length must be between 5 and 255
            characters.
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

    def validate_identifier(self, identifier: str) -> str:
        """Validate the raw ``identifier`` field value.

        Ensures the provided value is a syntactically valid email
        address or phone number. Any other value is rejected.

        Args:
            identifier (str): The raw identifier provided by the client.

        Returns:
            str: The validated identifier, unchanged.

        Raises:
            InputError: If the identifier is neither a valid email
                address nor a valid phone number.
        """
        if not (
            is_valid_email(identifier=identifier)
            or is_valid_phone(identifier=identifier)
        ):
            raise self.raise_input_error(InvalidIdentifier(identifier=identifier))

        return identifier
