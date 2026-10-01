"""Provides base error definition classes for different error categories.

This module defines foundational error definition classes that serve as
category-specific base classes for various error types including application,
authentication, business logic, database, external services, HTTP, system,
and validation errors.

IMPORTANT - What these classes represent:
    - These are BASE ERROR DEFINITION categories (blueprints), NOT exceptions
    - Each definition declares common defaults for its error category
    - They define the default error code, HTTP status, message template, and retryability
    - Specific error definitions inherit from these to provide specialized behavior

Key distinction:
    - ErrorDefinition classes = "WHAT the error category looks like" (blueprint)
    - Specific error classes = concrete error definitions for specific scenarios
    - Exception classes = "WHEN the error happens" (raised in code flow)
"""

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.base import ErrorDefinition


class AppErrorDefinition(ErrorDefinition):
    """Base error definition for general application errors.

    This is the base class for application-level errors that don't fit
    into more specific categories. It provides default error handling
    behavior for general application issues.

    Attributes:
        code: "APP:ERROR"
        http_status: 500 Internal Server Error
        message_template: "The application encountered an error."
        is_retryable: False

    Example:
        >>> # Subclass this for application-specific errors
        ... class MyAppError(AppErrorDefinition):
        ...     code = "MY_APP_ERROR"
        ...     http_status = 400
    """

    code = "APP:ERROR"
    http_status = 500
    message_template = _n("The application encountered an error.")
    is_retryable = False


class AuthErrorDefinition(ErrorDefinition):
    """Base error definition for authentication and authorization errors.

    This is the base class for all authentication and authorization-related
    errors. It provides default error handling behavior for authentication
    failures.

    Attributes:
        code: "AUTH:ERROR"
        http_status: 401 Unauthorized
        message_template: "Authentication could not be completed."
        is_retryable: False

    Example:
        >>> # Subclass this for authentication-specific errors
        ... class InvalidToken(AuthErrorDefinition):
        ...     code = "AUTH_INVALID_TOKEN"
    """

    code = "AUTH:ERROR"
    http_status = 401
    message_template = _n("Authentication could not be completed.")
    is_retryable = False


class BizErrorDefinition(ErrorDefinition):
    """Base error definition for business logic violations.

    This is the base class for all business logic-related errors.
    It provides default error handling behavior for business rule
    violations and domain-specific constraints.

    Attributes:
        code: "BIZ:ERROR"
        http_status: 422 Unprocessable Entity
        message_template: "The operation violates business rules."
        is_retryable: False

    Example:
        >>> # Subclass this for business logic-specific errors
        ... class InsufficientFunds(BizErrorDefinition):
        ...     code = "BIZ_INSUFFICIENT_FUNDS"
    """

    code = "BIZ:ERROR"
    http_status = 422
    message_template = _n("The operation violates business rules.")
    is_retryable = False


class DbErrorDefinition(ErrorDefinition):
    """Base error definition for database operation failures.

    This is the base class for all database-related errors including
    connection issues, query failures, constraint violations, and
    data integrity problems.

    Attributes:
        code: "DB:ERROR"
        http_status: 500 Internal Server Error
        message_template: "The database operation failed."
        is_retryable: False

    Example:
        >>> # Subclass this for database-specific errors
        ... class DuplicateEntry(DbErrorDefinition):
        ...     code = "DB_DUPLICATE_ENTRY"
    """

    code = "DB:ERROR"
    http_status = 500
    message_template = _n("The database operation failed.")
    is_retryable = False


class ExtErrorDefinition(ErrorDefinition):
    """Base error definition for external service failures.

    This is the base class for errors that occur when interacting with
    external services, APIs, or third-party systems.

    Attributes:
        code: "EXT:ERROR"
        http_status: 502 Bad Gateway
        message_template: "The external service request failed."
        is_retryable: False

    Example:
        >>> # Subclass this for external service-specific errors
        ... class PaymentGatewayError(ExtErrorDefinition):
        ...     code = "EXT_PAYMENT_GATEWAY_ERROR"
    """

    code = "EXT:ERROR"
    http_status = 502
    message_template = _n("The external service request failed.")
    is_retryable = False


class HttpErrorDefinition(ErrorDefinition):
    """Base error definition for HTTP request processing errors.

    This is the base class for HTTP-related errors including malformed
    requests, unsupported methods, and invalid HTTP headers.

    Attributes:
        code: "HTTP:ERROR"
        http_status: 400 Bad Request
        message_template: "The HTTP request could not be processed."
        is_retryable: False

    Example:
        >>> # Subclass this for HTTP-specific errors
        ... class UnsupportedMediaType(HttpErrorDefinition):
        ...     code = "HTTP_UNSUPPORTED_MEDIA_TYPE"
    """

    code = "HTTP:ERROR"
    http_status = 400
    message_template = _n("The HTTP request could not be processed.")
    is_retryable = False


class SysErrorDefinition(ErrorDefinition):
    """Base error definition for system-level internal errors.

    This is the base class for system-level errors including infrastructure
    issues, resource exhaustion, and unexpected system failures.

    Attributes:
        code: "SYS:ERROR"
        http_status: 500 Internal Server Error
        message_template: "The system encountered an internal error."
        is_retryable: False

    Example:
        >>> # Subclass this for system-specific errors
        ... class ResourceExhaustion(SysErrorDefinition):
        ...     code = "SYS_RESOURCE_EXHAUSTION"
    """

    code = "SYS:ERROR"
    http_status = 500
    message_template = _n("The system encountered an internal error.")
    is_retryable = False


class ValidErrorDefinition(ErrorDefinition):
    """Base error definition for data validation failures.

    This is the base class for validation-related errors that occur when
    input data fails to meet validation rules or constraints.

    Attributes:
        code: "VALID:ERROR"
        http_status: 400 Bad Request
        message_template: "The provided data failed validation."
        is_retryable: False

    Example:
        >>> # Subclass this for validation-specific errors
        ... class InvalidEmailFormat(ValidErrorDefinition):
        ...     code = "VALID_INVALID_EMAIL_FORMAT"
    """

    code = "VALID:ERROR"
    http_status = 400
    message_template = _n("The provided data failed validation.")
    is_retryable = False
