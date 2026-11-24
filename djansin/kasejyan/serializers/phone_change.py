"""Serializers for the phone-change flow.

Exposes two DRF serializers:

* :class:`RequestChangePhoneSerializer` — validates the payload for
  requesting a verification code to be sent to the new phone number.
* :class:`ChangePhoneSerializer` — validates the payload for confirming
  the change with that code.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat
from core.serializers import Serializer
from core.utils.user_identifier import is_valid_phone


class RequestChangePhoneSerializer(Serializer):
    """Serializer validating the payload for requesting a phone-change code.

    Accepts a single write-only ``new_phone`` number. Field-level
    validation enforces presence and syntactic validity; the
    "not already owned" rule and code dispatch are handled by the
    service layer.

    Attributes:
        new_phone (serializers.CharField): Write-only phone number that
            should replace the current one.
    """

    new_phone = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("New phone number is required."),
            "blank": _t("New phone number cannot be blank."),
            "null": _t("New phone number cannot be null."),
        },
    )

    def validate_new_phone(self, new_phone: str) -> str:
        """Validate the raw ``new_phone`` field value.

        Ensures the value satisfies the project's phone-number format
        rules. Deeper checks (ownership, existence) are delegated to
        the service layer.

        Args:
            new_phone (str): The raw phone number provided by the client.

        Returns:
            str: The validated phone number, unchanged.

        Raises:
            InputError: If the phone number does not conform to the
                expected format.
        """
        if not is_valid_phone(identifier=new_phone):
            raise self.raise_input_error(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        return new_phone


class ChangePhoneSerializer(Serializer):
    """Serializer validating the payload for confirming a phone change.

    Accepts the new phone number and the six-digit verification code
    that was sent to it. Field-level validation enforces presence and
    syntactic validity; the "not already owned by another user" rule,
    the code's purpose and validity, and the atomic swap are all handled
    by the service layer.

    Attributes:
        new_phone (serializers.CharField): Write-only new phone number
            that should replace the current one.
        code (serializers.CharField): Write-only six-digit verification
            code that was sent to ``new_phone``.
    """

    new_phone = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("New phone number is required."),
            "blank": _t("New phone number cannot be blank."),
            "null": _t("New phone number cannot be null."),
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

    def validate_new_phone(self, new_phone: str) -> str:
        """Validate the raw ``new_phone`` field value.

        Ensures the value satisfies the project's phone-number format
        rules. Deeper checks (ownership, existence) are delegated to
        the service layer.

        Args:
            new_phone (str): The raw phone number provided by the client.

        Returns:
            str: The validated phone number, unchanged.

        Raises:
            InputError: If the phone number does not conform to the
                expected format.
        """
        if not is_valid_phone(identifier=new_phone):
            raise self.raise_input_error(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        return new_phone


class PhoneChangeResultSerializer(Serializer):
    """Payload of a successful phone change."""

    username = serializers.CharField()
    old_phone = serializers.CharField(allow_null=True)
    new_phone = serializers.CharField()
    changed_at = serializers.DateTimeField()


class PhoneChangeEnvelopeSerializer(Serializer):
    """Envelope for ``ChangePhoneView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = PhoneChangeResultSerializer()


class PhoneChangeRequestResultSerializer(Serializer):
    """Payload of a successful phone-change code request."""

    new_phone = serializers.CharField()
    expires_at = serializers.DateTimeField()


class PhoneChangeRequestEnvelopeSerializer(Serializer):
    """Envelope for ``RequestChangePhoneView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = PhoneChangeRequestResultSerializer()
