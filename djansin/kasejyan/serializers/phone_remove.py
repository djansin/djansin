"""Serializers for the phone-removal flow.

Exposes two DRF serializers:

* :class:`RequestRemovePhoneSerializer` — validates the payload for
  requesting a verification code to be sent to the phone being removed.
* :class:`RemovePhoneSerializer` — validates the payload for confirming
  the removal with that code.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework import serializers

from core.exceptions.errors.validation import InvalidFormat
from core.serializers import Serializer
from core.utils.user_identifier import is_valid_phone


class RequestRemovePhoneSerializer(Serializer):
    """Serializer validating the payload for requesting a phone-removal code.

    Accepts a single write-only ``phone`` number. Field-level validation
    enforces presence and syntactic validity; ownership, the "last login
    method" guard, and the "no still-valid code" rule are enforced by
    the service layer.

    Attributes:
        phone (serializers.CharField): Write-only phone number whose
            removal is being requested.
    """

    phone = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("Phone number is required."),
            "blank": _t("Phone number cannot be blank."),
            "null": _t("Phone number cannot be null."),
        },
    )

    def validate_phone(self, phone: str) -> str:
        """Validate the raw ``phone`` field value.

        Ensures the value satisfies the project's phone-number format
        rules. Deeper checks (ownership, existence) are delegated to
        the service layer.

        Args:
            phone (str): The raw phone number provided by the client.

        Returns:
            str: The validated phone number, unchanged.

        Raises:
            InputError: If the phone number does not conform to the
                expected format.
        """
        if not is_valid_phone(identifier=phone):
            raise self.raise_input_error(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        return phone


class RemovePhoneSerializer(Serializer):
    """Serializer validating the payload for removing a phone number.

    Accepts the phone number to detach from the authenticated user's
    account, together with the six-digit verification code that was
    dispatched to that number. Field-level validation enforces presence,
    length, and syntactic validity; ownership, the "last login method"
    guard, the code's purpose and validity, and the atomic detach are
    all enforced by the service layer.

    Attributes:
        phone (serializers.CharField): Write-only phone number to remove.
        code (serializers.CharField): Write-only six-digit verification
            code that was sent to ``phone``.
    """

    phone = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        error_messages={
            "required": _t("Phone number is required."),
            "blank": _t("Phone number cannot be blank."),
            "null": _t("Phone number cannot be null."),
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

    def validate_phone(self, phone: str) -> str:
        """Validate the raw ``phone`` field value.

        Ensures the value satisfies the project's phone-number format
        rules. Deeper checks (ownership, existence) are delegated to
        the service layer.

        Args:
            phone (str): The raw phone number provided by the client.

        Returns:
            str: The validated phone number, unchanged.

        Raises:
            InputError: If the phone number does not conform to the
                expected format.
        """
        if not is_valid_phone(identifier=phone):
            raise self.raise_input_error(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        return phone


class PhoneRemovalResultSerializer(Serializer):
    """Payload of a successful phone removal."""

    username = serializers.CharField()
    removed_phone = serializers.CharField()
    removed_at = serializers.DateTimeField()


class PhoneRemovalEnvelopeSerializer(Serializer):
    """Envelope for ``RemovePhoneView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = PhoneRemovalResultSerializer()


class PhoneRemovalRequestResultSerializer(Serializer):
    """Payload of a successful phone-removal code request."""

    phone = serializers.CharField()
    expires_at = serializers.DateTimeField()


class PhoneRemovalRequestEnvelopeSerializer(Serializer):
    """Envelope for ``RequestRemovePhoneView`` (200 OK)."""

    message = serializers.CharField()
    code = serializers.CharField()
    data = PhoneRemovalRequestResultSerializer()
