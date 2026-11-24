"""Error envelope serializers for drf-spectacular documentation.

These serializers describe the shape of error responses produced by the
project's exception handlers. They are **not** used at runtime — they
exist solely to give drf-spectacular enough metadata to render accurate
error schemas in the OpenAPI document.
"""

from rest_framework import serializers

from core.serializers import Serializer


class FieldErrorsSerializer(Serializer):
    """Per-field validation errors, keyed by field name."""

    # Open-ended: each key is a field name, each value is a list of messages.
    # Use JSONField so Swagger renders it as a free-form object.
    pass  # fields are dynamic; documented via description


class ErrorDetailSerializer(Serializer):
    """Detail payload for domain and validation errors."""

    field_errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
        help_text="Mapping of field name → list of error messages.",
    )
    non_field_errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Errors not tied to a specific field.",
    )


class ErrorEnvelopeSerializer(Serializer):
    """Standard error envelope returned by the project's exception handler.

    Example::

        {
          "code": "VALID:VALIDATION_ERROR",
          "http_status": 422,
          "message": "Validation failed. Please check your input.",
          "is_retryable": false,
          "detail": {
            "field_errors": {},
            "non_field_errors": ["..."]
          }
        }
    """

    code = serializers.CharField(
        help_text="Machine-readable error code, e.g. ``VALID:VALIDATION_ERROR``."
    )
    http_status = serializers.IntegerField(
        help_text="HTTP status code mirroring the response status."
    )
    message = serializers.CharField(help_text="Human-readable error message.")
    is_retryable = serializers.BooleanField(
        help_text="Whether the client may retry the same request."
    )
    detail = ErrorDetailSerializer(
        required=False, help_text="Structured detail; shape varies by error category."
    )
