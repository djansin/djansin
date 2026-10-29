"""Provides DRF exception wrappers that integrate with the error definition framework.

This module defines error classes that wrap Django REST Framework's built-in
exceptions, converting them to the standardized error format used throughout
the application. Each DRF exception is mapped to an appropriate error category
with proper HTTP status codes and message templates.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a DRF error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exception handlers use these definitions for consistent API responses

Key distinction:
    - ErrorDefinition classes = "WHAT the DRF error looks like" (blueprint)
    - DRF exceptions = raised by DRF framework, converted via custom handler

Common patterns:
    - Validation errors return 422 with field/non-field error details
    - Authentication errors return 401/403 based on failure type
    - Rate limiting is retryable with wait time information
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors import AppErrorDefinition
from core.exceptions.errors.auth import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
)
from core.exceptions.errors.business import Throttled
from core.exceptions.errors.http import (
    MethodNotAllowed,
    NotFound,
    ParserError,
    UnsupportedMediaType,
)
from core.exceptions.errors.validation import Validation


class APIError(AppErrorDefinition):
    """Error definition for generic/unhandled API exceptions.

    This error definition serves as a fallback for APIException instances
    that are not explicitly mapped to specific error types. It preserves the
    original HTTP status code from the exception when possible.

    Attributes:
        code: API_ERROR
        http_status: 500 Internal Server Error (overridden by exception's status_code)
        message_template: API request failed. {detail}
        is_retryable: False
    """

    code = "API_ERROR"
    http_status = 500
    message_template = _n("API request failed. {detail}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        detail: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a generic API error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ErrorCodes:
    """Central registry of DRF exception error definitions.

    This class provides a convenient namespace for accessing DRF error
    definition classes throughout the application.

    Attributes:
        DRF_VALIDATION_ERROR: DRF validation error definition
        DRF_PERMISSION_DENIED: DRF permission denied definition
        DRF_NOT_FOUND: DRF 404 not found definition
        DRF_AUTHENTICATION_FAILED: DRF auth failed definition
        DRF_NOT_AUTHENTICATED: DRF not authenticated definition
        DRF_METHOD_NOT_ALLOWED: DRF method not allowed definition
        DRF_UNSUPPORTED_MEDIA_TYPE: DRF unsupported media type definition
        DRF_THROTTLED: DRF rate limiting definition
        DRF_PARSE_ERROR: DRF parse error definition
        DRF_GENERIC_API_ERROR: Generic fallback for unhandled DRF exceptions
    """

    # ===== DRF Exceptions =====
    DRF_VALIDATION = Validation
    DRF_PERMISSION_DENIED = PermissionDenied
    DRF_NOT_FOUND = NotFound
    DRF_AUTHENTICATION_FAILED = AuthenticationFailed
    DRF_NOT_AUTHENTICATED = NotAuthenticated
    DRF_METHOD_NOT_ALLOWED = MethodNotAllowed
    DRF_UNSUPPORTED_MEDIA_TYPE = UnsupportedMediaType
    DRF_THROTTLED = Throttled
    DRF_PARSE_ERROR = ParserError
    DRF_GENERIC_API_ERROR = APIError
