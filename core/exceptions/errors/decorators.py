"""Provides a decorator for defining error definitions with standardized attributes.

This module offers a convenient decorator-based approach to creating error
definition classes, eliminating boilerplate code while maintaining consistency
across all error definitions in the application.

The `error_definition` decorator automatically assigns the common error attributes
(code, HTTP status, message template, and retryability) to any class that inherits
from `ErrorDefinition`. This reduces duplication and ensures all error definitions
follow the same pattern.
"""

from typing import TypeVar

from core.exceptions.errors.base import ErrorDefinition


ErrorDefinitionType = TypeVar("ErrorDefinitionType", bound=ErrorDefinition)


def error_definition(
    code: str,
    http_status: int,
    message_template: str,
    is_retryable: bool = False,
) -> type[ErrorDefinitionType]:
    """Creates a decorator that converts a class into a standardized error definition.

    This factory function returns a class decorator that automatically assigns the
    specified error attributes to the decorated class. The decorated class must
    inherit from `ErrorDefinition` (or a subclass thereof).

    The decorator is designed to be used with error definition classes to reduce
    boilerplate and ensure consistent attribute naming across the codebase. It
    follows the error definition pattern where each error defines:
        - A unique error code for identification
        - An HTTP status code for API responses
        - A human-readable message template with optional placeholders
        - A boolean indicating whether the operation can be retried

    Args:
        code: A unique error code string (e.g., "BIZ_INSUFFICIENT_FUNDS") used
            for error identification and client-side handling.
        http_status: The HTTP status code to return with this error
            (e.g., 400, 404, 422, 500).
        message_template: A human-readable message template that may contain
            placeholders (e.g., "Field '{field}' is required.") which will be
            formatted with context data at runtime.
        is_retryable: Whether the operation that caused this error can be
            retried. Defaults to False. Set to True for transient errors like
            rate limiting or connection timeouts.

    Returns:
        A class decorator function that applies the error attributes to the
        decorated class and returns it with proper type annotation.

    Example:
        >>> @error_definition(
        ...     code="BIZ_INSUFFICIENT_FUNDS",
        ...     http_status=422,
        ...     message_template="Insufficient funds. Required: {required} {currency}",
        ...     is_retryable=False,
        ... )
        ... class InsufficientFunds(ErrorDefinition):
        ...     pass

        >>> @error_definition(
        ...     code="HTTP_RATE_LIMITED",
        ...     http_status=429,
        ...     message_template="Too many requests. Try again in {retry_after} seconds.",
        ...     is_retryable=True,
        ... )
        ... class RateLimited(ErrorDefinition):
        ...     pass

    Note:
        The decorated class can still define its own `__init__` method to accept
        context parameters for message template formatting. The decorator only
        sets the class-level attributes.

    See Also:
        `ErrorDefinition`: The base class that all error definitions must extend.
    """

    def decorator(cls: ErrorDefinitionType) -> ErrorDefinitionType:
        cls.code = code
        cls.http_status = http_status
        cls.message_template = message_template
        cls.is_retryable = is_retryable
        return cls

    return decorator
