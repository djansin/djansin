"""Provides a custom DRF exception handler that converts DRF exceptions to standardized error responses.

This module implements a custom exception handler that wraps Django REST Framework's
default exception handler and transforms all DRF exceptions into a consistent
error format using the application's error definition framework. Each exception
type is mapped to an appropriate error class with proper HTTP status codes and
structured error details.
"""

from typing import Any

from django.core import exceptions as dj_exc
from django.core.cache import InvalidCacheBackendError
from django.core.signing import BadSignature, SignatureExpired
from django.db import DatabaseError, IntegrityError, OperationalError
from django.db.models import ProtectedError
from django.http import Http404
from django.urls.exceptions import NoReverseMatch, Resolver404
from django.utils.encoding import DjangoUnicodeDecodeError
from rest_framework import exceptions as rest_exc
from rest_framework.views import exception_handler

from contrib.django_.exceptions import ErrorCodes as dj_error_code
from core.exceptions.base import BaseAppException
from core.exceptions.errors import AppErrorDefinition
from core.views.responses import Response

from .exceptions import ErrorCodes as drf_error_code


def custom_exception_handler(exc: Any, context: Any) -> Response | None:
    """Custom exception handler that converts DRF exceptions to standardized error responses.

    This handler intercepts exceptions raised during DRF request processing and
    transforms them into a consistent error response format using the application's
    error definitions. It preserves the original HTTP status codes while providing
    structured error details including codes, messages, and retryability flags.

    Args:
        exc: The exception instance that was raised.
        context: The context dictionary containing the view and request.

    Returns:
        Response | None: A Django REST Framework Response object with standardized
            error data, or None if the exception cannot be handled.
    """
    response = exception_handler(exc, context)

    if response is None:
        # return
        return handle_non_drf_exceptions(exc=exc, context=context)

    error_instance = None

    # Validation Error
    if isinstance(exc, rest_exc.ValidationError):
        field_errors = {}
        non_field_errors = []
        for field, errors in response.data.items():
            if field == "non_field_errors":
                non_field_errors = errors
            else:
                field_errors[field] = errors

        error_instance = drf_error_code.DRF_VALIDATION(
            field_errors=field_errors, non_field_errors=non_field_errors
        )

    # Permission Denied
    elif isinstance(exc, rest_exc.PermissionDenied):
        error_instance = drf_error_code.DRF_PERMISSION_DENIED(exc.detail)

    # Not Found (404)
    elif isinstance(exc, (rest_exc.NotFound, Http404)):
        error_instance = drf_error_code.DRF_NOT_FOUND()

    # Authentication Failed
    elif isinstance(exc, rest_exc.AuthenticationFailed):
        detail = str(exc.detail) if str(exc) else "Invalid authentication credentials."
        error_instance = drf_error_code.DRF_AUTHENTICATION_FAILED(detail=detail)

    # Not Authenticated
    elif isinstance(exc, rest_exc.NotAuthenticated):
        error_instance = drf_error_code.DRF_NOT_AUTHENTICATED()

    # Method Not Allowed
    elif isinstance(exc, rest_exc.MethodNotAllowed):
        error_instance = drf_error_code.DRF_METHOD_NOT_ALLOWED(method=exc.method)

    # Unsupported Media Type
    elif isinstance(exc, rest_exc.UnsupportedMediaType):
        error_instance = drf_error_code.DRF_UNSUPPORTED_MEDIA_TYPE(
            media_type=exc.media_type
        )

    # Throttled (Rate Limiting)
    elif isinstance(exc, rest_exc.Throttled):
        wait = getattr(exc, "wait", 60)  # Default 60 seconds if not provided
        error_instance = drf_error_code.DRF_THROTTLED(wait=wait)

    # Parse Error (JSON malformed, etc.)
    elif isinstance(exc, rest_exc.ParseError):
        detail = str(exc) if str(exc) else "Invalid JSON or data format."
        error_instance = drf_error_code.DRF_PARSE_ERROR(detail=detail)

    # Generic DRF API Exception
    elif isinstance(exc, rest_exc.APIException):
        # Fallback for any other DRF exception
        error_instance = drf_error_code.DRF_GENERIC_API_ERROR()

    if error_instance:
        response.data = error_instance.to_dict()
        response.status_code = error_instance.http_status

    return response


def handle_non_drf_exceptions(exc: Any, context: Any) -> Response:
    """Handle Django core exceptions that DRF's default handler couldn't process.

    This handler converts Django core exceptions into standardized error responses
    using the application's error definitions, providing consistent error format
    across the entire application.

    Args:
        exc: The exception instance that was raised.
        context: The context dictionary containing the view and request.

    Returns:
        Response: A DRF Response object with standardized error data.

    Raises:
        Exception: Re-raises the exception if no handler is found (fallback).
    """
    error_instance = None

    # ===== HTTP & View Exceptions =====

    # Handle Django's Http404
    if isinstance(exc, Http404):
        error_instance = dj_error_code.DJANGO_404_NOT_FOUND()

    # Handle Django's PermissionDenied
    elif isinstance(exc, dj_exc.PermissionDenied):
        error_instance = dj_error_code.DJANGO_PERMISSION_DENIED()

    # Handle Bad Request (400)
    elif isinstance(exc, dj_exc.BadRequest):
        error_instance = dj_error_code.DJANGO_BAD_REQUEST()

    # ===== Suspicious Operation Exceptions =====

    # Handle general SuspiciousOperation
    elif isinstance(exc, dj_exc.SuspiciousOperation):
        error_instance = dj_error_code.DJANGO_SUSPICIOUS_OPERATION()

    # Handle SuspiciousFileOperation
    elif isinstance(exc, dj_exc.SuspiciousFileOperation):
        error_instance = dj_error_code.DJANGO_SUSPICIOUS_FILE_OPERATION()

    # Handle SuspiciousMultipartForm
    elif isinstance(exc, dj_exc.SuspiciousMultipartForm):
        error_instance = dj_error_code.DJANGO_SUSPICIOUS_MULTIPART_FORM()

    # Handle TooManyFieldsSent
    elif isinstance(exc, dj_exc.TooManyFieldsSent):
        error_instance = dj_error_code.DJANGO_TOO_MANY_FIELDS()

    # Handle RequestDataTooBig
    elif isinstance(exc, dj_exc.RequestDataTooBig):
        error_instance = dj_error_code.DJANGO_REQUEST_DATA_TOO_BIG()

    # ===== Database Exceptions =====

    # Handle general DatabaseError
    elif isinstance(exc, DatabaseError):
        error_instance = dj_error_code.DJANGO_DATABASE_ERROR()

    # Handle IntegrityError (constraint violations)
    elif isinstance(exc, IntegrityError):
        error_instance = dj_error_code.DJANGO_INTEGRITY_ERROR()

    # Handle OperationalError (connection issues, deadlocks)
    elif isinstance(exc, OperationalError):
        error_instance = dj_error_code.DJANGO_OPERATIONAL_ERROR()

    # Handle ProtectedError (when deleting a protected object)
    elif isinstance(exc, ProtectedError):
        # Extract model name and protected objects from exception
        model_name = (
            exc.protected_objects.model.__name__ if exc.protected_objects else None
        )
        error_instance = dj_error_code.DJANGO_PROTECTED_ERROR(model_name=model_name)

    # ===== ORM & Model Exceptions =====

    # Handle ObjectDoesNotExist
    elif isinstance(exc, dj_exc.ObjectDoesNotExist):
        # Extract model name from exception if available
        model_name = exc.__class__.__name__.replace("DoesNotExist", "")
        error_instance = dj_error_code.DJANGO_OBJECT_DOES_NOT_EXIST(
            model_name=model_name
        )

    # Handle MultipleObjectsReturned
    elif isinstance(exc, dj_exc.MultipleObjectsReturned):
        model_name = exc.__class__.__name__.replace("MultipleObjectsReturned", "")
        error_instance = dj_error_code.DJANGO_MULTIPLE_OBJECTS_RETURNED(
            model_name=model_name
        )

    # Handle FieldError
    elif isinstance(exc, dj_exc.FieldError):
        error_instance = dj_error_code.DJANGO_FIELD_ERROR(detail=str(exc))

    # ===== Validation Exceptions =====

    # Handle Django's ValidationError
    elif isinstance(exc, dj_exc.ValidationError):
        # Parse ValidationError to extract field errors
        field_errors = {}
        non_field_errors = []

        if hasattr(exc, "error_dict"):
            # Form validation error with field-specific errors
            for field, errors in exc.error_dict.items():
                field_errors[field] = [str(e) for e in errors]
        elif hasattr(exc, "error_list"):
            # List of errors (non-field specific)
            non_field_errors = [str(e) for e in exc.error_list]
        else:
            # Simple string error
            non_field_errors = [str(exc)]

        error_instance = dj_error_code.DJANGO_VALIDATION_ERROR(
            detail="Validation failed.",
            field_errors=field_errors,
            non_field_errors=non_field_errors,
        )

    # ===== URL & Routing Exceptions =====

    # Handle Resolver404
    elif isinstance(exc, Resolver404):
        error_instance = dj_error_code.DJANGO_RESOLVER_404()

    # Handle NoReverseMatch
    elif isinstance(exc, NoReverseMatch):
        error_instance = dj_error_code.DJANGO_NO_REVERSE_MATCH()

    # ===== Configuration & Setup Exceptions =====

    # Handle ImproperlyConfigured
    elif isinstance(exc, dj_exc.ImproperlyConfigured):
        error_instance = dj_error_code.DJANGO_IMPROPERLY_CONFIGURED(detail=str(exc))

    # Handle MiddlewareNotUsed
    elif isinstance(exc, dj_exc.MiddlewareNotUsed):
        error_instance = dj_error_code.DJANGO_MIDDLEWARE_NOT_USED()

    # Handle AppRegistryNotReady
    elif isinstance(exc, dj_exc.AppRegistryNotReady):
        error_instance = dj_error_code.DJANGO_APP_REGISTRY_NOT_READY()

    # ===== Encoding & Data Exceptions =====

    # Handle DjangoUnicodeDecodeError
    elif isinstance(exc, DjangoUnicodeDecodeError):
        error_instance = dj_error_code.DJANGO_UNICODE_DECODE_ERROR()

    # ===== Cache Exceptions =====

    # Handle InvalidCacheBackendError
    elif isinstance(exc, InvalidCacheBackendError):
        error_instance = dj_error_code.DJANGO_INVALID_CACHE_BACKEND()

    # ===== Signing Exceptions =====

    # Handle BadSignature
    elif isinstance(exc, BadSignature):
        error_instance = dj_error_code.DJANGO_BAD_SIGNATURE()

    # Handle SignatureExpired
    elif isinstance(exc, SignatureExpired):
        error_instance = dj_error_code.DJANGO_SIGNATURE_EXPIRED()

    elif isinstance(exc, BaseAppException):
        error_instance = exc

    # ===== Generic Fallback =====
    # If none of the above matched, re-raise the exception
    else:
        error_instance = AppErrorDefinition()

    # Convert error instance to DRF Response
    if error_instance:
        return Response(
            data=error_instance.to_dict(),
            status=error_instance.http_status,
        )
