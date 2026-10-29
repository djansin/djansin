"""Provides comprehensive exception handling for Django applications.

This module implements a robust exception handler that converts various exception
types into standardized API responses using the error definition framework.
It handles:
- Custom BaseAppException hierarchy (Auth, Validation, Business, HTTP, Database, etc.)
- Django's Http404 and PermissionDenied
- Django REST Framework's APIException
- Validation errors from DRF serializers
- Unexpected exceptions (fallback to generic error)
"""

import logging
import traceback
from functools import wraps
from typing import Any, Dict, Union

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    Throttled,
    ValidationError as DRFValidationError,
)
from rest_framework.views import exception_handler as drf_handler

# Import your exception classes and error codes
from core.exceptions import BaseAppException, ExceptionSeverity
from core.exceptions.errors import ErrorCodes
from core.exceptions.errors.validation import InvalidUsername


logger = logging.getLogger(__name__)


class ExceptionHandler:
    """Centralized exception handler for converting exceptions to API responses.

    This handler processes exceptions raised during request processing and
    returns appropriate JSON responses with standardized error format.

    Features:
        - Handles custom BaseAppException hierarchy
        - Converts Django exceptions to consistent format
        - Logs errors with appropriate severity levels
        - Preserves error details for debugging when appropriate
        - Falls back to generic error for unexpected exceptions
    """

    # Default error for when no specific mapping exists
    DEFAULT_ERROR = ErrorCodes.APP_ERROR

    def __init__(self, debug: bool = False) -> None:
        """Initialize the exception handler.

        Args:
            debug: If True, include traceback and full error details in responses.
                   Should be False in production for security.
        """
        self.debug = debug

    def handle(self, exc: Exception, request: HttpRequest = None) -> HttpResponse:
        """Main entry point for handling exceptions.

        Args:
            exc: The exception that was raised.
            request: The HTTP request that caused the exception (optional).

        Returns:
            HttpResponse: A JSON response with standardized error format.
        """
        # Handle custom BaseAppException hierarchy
        if isinstance(exc, BaseAppException):
            return self._handle_app_exception(exc, request)

        # Handle Django's Http404
        if isinstance(exc, Http404):
            return self._handle_http404(exc, request)

        # Handle Django's PermissionDenied
        if isinstance(exc, PermissionDenied):
            return self._handle_permission_denied(exc, request)

        # Handle Django REST Framework exceptions (if DRF is installed)
        try:
            if isinstance(exc, APIException):
                return self._handle_drf_exception(exc, request)
        except ImportError:
            pass

        # Handle any other unexpected exceptions
        return self._handle_unexpected_exception(exc, request)

    def _handle_app_exception(
        self, exc: BaseAppException, request: HttpRequest = None
    ) -> JsonResponse:
        """Handle custom BaseAppException instances.

        Args:
            exc: The BaseAppException instance.
            request: The HTTP request (optional).

        Returns:
            JsonResponse: Standardized error response.
        """
        error_instance = exc.error
        severity = exc.severity

        # Log based on severity
        self._log_exception(
            exc=exc,
            severity=severity,
            request=request,
            error_code=error_instance.code,
            context=(
                error_instance._format_kwargs
                if hasattr(error_instance, "_format_kwargs")
                else {}
            ),
        )

        # Build response data
        response_data = error_instance.to_dict()

        # Add request ID if available
        request_id = self._get_request_id(request)
        if request_id:
            response_data["request_id"] = request_id

        # Add traceback in debug mode for server errors
        if self.debug and severity in {
            ExceptionSeverity.ERROR,
            ExceptionSeverity.CRITICAL,
            ExceptionSeverity.FATAL,
        }:
            response_data["traceback"] = traceback.format_exc()

        # Determine HTTP status code
        status_code = error_instance.http_status

        return JsonResponse(response_data, status=status_code)

    def _handle_http404(
        self, exc: Http404, request: HttpRequest = None
    ) -> JsonResponse:
        """Handle Django's Http404 exception.

        Args:
            exc: The Http404 exception.
            request: The HTTP request (optional).

        Returns:
            JsonResponse: 404 error response.
        """
        logger.info(
            "HTTP 404: %s",
            request.path if request else "Unknown path",
            extra={"request_path": request.path if request else None},
        )

        error = ErrorCodes.HTTP_NOT_FOUND(resource=_("Requested resource"))

        response_data = error.to_dict()
        response_data["request_id"] = self._get_request_id(request)

        return JsonResponse(response_data, status=404)

    def _handle_permission_denied(
        self, exc: PermissionDenied, request: HttpRequest = None
    ) -> JsonResponse:
        """Handle Django's PermissionDenied exception.

        Args:
            exc: The PermissionDenied exception.
            request: The HTTP request (optional).

        Returns:
            JsonResponse: 403 error response.
        """
        logger.warning(
            "Permission denied: %s",
            request.path if request else "Unknown path",
            extra={
                "request_path": request.path if request else None,
                "user": (
                    str(request.user) if request and hasattr(request, "user") else None
                ),
            },
        )

        error = ErrorCodes.HTTP_FORBIDDEN()

        response_data = error.to_dict()
        response_data["request_id"] = self._get_request_id(request)

        return JsonResponse(response_data, status=403)

    def _handle_drf_exception(
        self, exc: Exception, request: HttpRequest = None
    ) -> HttpResponse:
        """Handle Django REST Framework exceptions.

        This method uses DRF's default handler as a base but enriches
        the response with our standard error format when possible.

        Args:
            exc: The DRF APIException instance.
            request: The HTTP request (optional).

        Returns:
            HttpResponse: Error response (typically from DRF handler or fallback).
        """
        try:
            response = drf_handler(exc, request)

            if response is not None:
                # Map DRF status codes to our error codes
                status_code = response.status_code

                # Try to map to appropriate error definition
                error = self._map_drf_exception_to_error(exc, status_code)

                # Preserve DRF's validation error details if they exist
                if hasattr(response, "data") and isinstance(response.data, dict):
                    if "field_errors" not in error.details and response.data:
                        # Create a new error instance with DRF's validation details
                        if (
                            isinstance(response.data, dict)
                            and "detail" not in response.data
                        ):
                            # This is likely a validation error with field errors
                            error = InvalidUsername(field_errors=response.data)

                response_data = error.to_dict()
                response_data["request_id"] = self._get_request_id(request)

                if self.debug:
                    response_data["traceback"] = traceback.format_exc()

                response.data = response_data
                return response

        except ImportError:
            pass

        # Fallback if DRF not available or handler fails
        return self._handle_unexpected_exception(exc, request)

    def _map_drf_exception_to_error(self, exc: Exception, status_code: int) -> Any:
        """Map DRF exception to appropriate error definition.

        Args:
            exc: The DRF exception.
            status_code: The HTTP status code.

        Returns:
            ErrorDefinition: Appropriate error definition instance.
        """
        # Authentication errors
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            return ErrorCodes.AUTH_INVALID_TOKEN()

        # Permission errors
        if isinstance(exc, DRFPermissionDenied):
            return ErrorCodes.HTTP_FORBIDDEN()

        # Not found
        if isinstance(exc, NotFound):
            return ErrorCodes.HTTP_NOT_FOUND(resource=_("Resource"))

        # Method not allowed
        if isinstance(exc, MethodNotAllowed):
            return ErrorCodes.HTTP_METHOD_NOT_ALLOWED(
                method=exc.method if hasattr(exc, "method") else "UNKNOWN",
                allowed_methods=(
                    exc.allowed_methods if hasattr(exc, "allowed_methods") else []
                ),
            )

        # Throttled
        if isinstance(exc, Throttled):
            wait = exc.wait if hasattr(exc, "wait") else 60
            return ErrorCodes.BIZ_RATE_LIMITED(retry_after=wait)

        # Validation errors - special handling
        if isinstance(exc, DRFValidationError):
            # Use the more detailed validation error structure
            return InvalidUsername(field_errors=getattr(exc, "detail", {}))

        # Default mapping based on status code
        status_map = {
            400: ErrorCodes.HTTP_BAD_REQUEST,
            401: ErrorCodes.HTTP_UNAUTHORIZED,
            403: ErrorCodes.HTTP_FORBIDDEN,
            404: ErrorCodes.HTTP_NOT_FOUND,
            405: ErrorCodes.HTTP_METHOD_NOT_ALLOWED,
            409: ErrorCodes.HTTP_CONFLICT,
            429: ErrorCodes.BIZ_RATE_LIMITED,
            500: ErrorCodes.SYS_INTERNAL_ERROR,
            502: ErrorCodes.EXT_API_ERROR,
            503: ErrorCodes.SYS_SERVICE_UNAVAILABLE,
            504: ErrorCodes.SYS_TIMEOUT,
        }

        error_class = status_map.get(status_code, ErrorCodes.SYS_INTERNAL_ERROR)

        if error_class == ErrorCodes.HTTP_BAD_REQUEST:
            return error_class(details=str(exc) if exc else "Invalid request")

        if error_class == ErrorCodes.HTTP_NOT_FOUND:
            return error_class(resource=_("Resource"))

        if error_class == ErrorCodes.BIZ_RATE_LIMITED:
            return error_class(retry_after=60)

        return error_class()

    def _handle_unexpected_exception(
        self, exc: Exception, request: HttpRequest = None
    ) -> JsonResponse:
        """Handle unexpected exceptions that weren't caught by other handlers.

        Args:
            exc: The unexpected exception.
            request: The HTTP request (optional).

        Returns:
            JsonResponse: 500 error response with generic message.
        """
        # Log with full traceback for unexpected errors
        logger.error(
            "Unexpected exception: %s",
            str(exc),
            exc_info=True,
            extra={
                "request_path": request.path if request else None,
                "request_method": request.method if request else None,
            },
        )

        error = ErrorCodes.SYS_UNKNOWN_ERROR(reference_id=self._generate_error_id())

        response_data = error.to_dict()
        response_data["request_id"] = self._get_request_id(request)

        if self.debug:
            response_data["exception_type"] = type(exc).__name__
            response_data["exception_message"] = str(exc)
            response_data["traceback"] = traceback.format_exc()

        return JsonResponse(response_data, status=500)

    def _log_exception(
        self,
        exc: Exception,
        severity: ExceptionSeverity,
        request: HttpRequest = None,
        error_code: str = None,
        context: Dict[str, Any] = None,
    ) -> None:
        """Log exception with appropriate severity level.

        Args:
            exc: The exception to log.
            severity: The severity level of the exception.
            request: The HTTP request (optional).
            error_code: The error code associated with the exception.
            context: Additional context information for logging.
        """
        log_extra = {
            "error_code": error_code,
            "severity": severity.name,
            "request_path": request.path if request else None,
            "request_method": request.method if request else None,
            "context": context or {},
        }

        if request and hasattr(request, "user"):
            log_extra["user"] = str(request.user)

        if severity == ExceptionSeverity.DEBUG:
            logger.debug(str(exc), extra=log_extra)
        elif severity == ExceptionSeverity.INFO:
            logger.info(str(exc), extra=log_extra)
        elif severity == ExceptionSeverity.WARNING:
            logger.warning(str(exc), extra=log_extra)
        elif severity == ExceptionSeverity.ERROR:
            logger.error(str(exc), exc_info=True, extra=log_extra)
        elif severity in (ExceptionSeverity.CRITICAL, ExceptionSeverity.FATAL):
            logger.critical(str(exc), exc_info=True, extra=log_extra)

    def _get_request_id(self, request: HttpRequest = None) -> str:
        """Extract request ID from request for tracking.

        Args:
            request: The HTTP request.

        Returns:
            str: Request ID if available, otherwise None.
        """
        if request and hasattr(request, "id"):
            return str(request.id)
        return None

    def _generate_error_id(self) -> str:
        """Generate a unique error ID for tracking.

        Returns:
            str: A unique identifier for the error.
        """
        import uuid

        return str(uuid.uuid4())[:8]


# Singleton instance with configurable debug mode
_default_handler = None


def get_exception_handler(debug: bool = None) -> ExceptionHandler:
    """Get or create the global exception handler instance.

    Args:
        debug: Force debug mode (if None, uses Django settings DEBUG).

    Returns:
        ExceptionHandler: The global exception handler instance.
    """
    global _default_handler
    if _default_handler is None:
        # Try to get DEBUG setting from Django
        try:
            debug_mode = debug if debug is not None else settings.DEBUG
        except ImportError:
            debug_mode = debug if debug is not None else False

        _default_handler = ExceptionHandler(debug=debug_mode)

    return _default_handler


def exception_handler(exc: Exception, context: dict = None) -> HttpResponse:
    """Django-compatible exception handler function.

    This function follows the Django exception handler signature and can be
    used with DRF's exception handler configuration or as a custom middleware.

    Args:
        exc: The exception that was raised.
        context: Dictionary containing context about the exception
                (typically includes 'request' and 'view').

    Returns:
        HttpResponse: JSON response with error details, or None if not handled.
    """
    request = context.get("request") if context else None
    handler = get_exception_handler()
    return handler.handle(exc, request)


# ===== Middleware for Django =====


class ExceptionHandlerMiddleware:
    """Django middleware for catching and handling exceptions globally.

    This middleware catches all exceptions raised during request processing
    and converts them to standardized JSON responses.

    Usage:
        Add to MIDDLEWARE in settings.py:
        'core.exceptions.handler.ExceptionHandlerMiddleware'
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.handler = get_exception_handler()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and handle any exceptions.

        Args:
            request: The HTTP request.

        Returns:
            HttpResponse: The response, possibly converted from an exception.
        """
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            return self.handler.handle(exc, request)


# ===== Convenience decorators =====


def handle_exceptions(view_func):
    """Decorator to wrap view functions with exception handling.

    This decorator catches exceptions raised in the view and returns
    standardized API responses.

    Usage:
        @handle_exceptions
        def my_view(request):
            ...
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        handler = get_exception_handler()
        try:
            return view_func(request, *args, **kwargs)
        except Exception as exc:
            return handler.handle(exc, request)

    return wrapper


# ===== DRF Settings Helper =====


def configure_drf_exception_handler(settings):
    """Helper to configure Django REST Framework to use our exception handler.

    This function returns the appropriate DRF exception handler configuration.

    Usage:
        In settings.py:
        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'core.exceptions.handler.configure_drf_exception_handler()',
        }
    """
    return "core.exceptions.handler.exception_handler"


__all__ = [
    "ExceptionHandler",
    "exception_handler",
    "get_exception_handler",
    "ExceptionHandlerMiddleware",
    "handle_exceptions",
    "configure_drf_exception_handler",
]
