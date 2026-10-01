"""Provides system-level error definitions for internal infrastructure issues.

This module defines concrete error definition classes for system-level
errors including unknown errors, internal server errors, service
unavailability, timeouts, and user creation failures.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a system error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like SystemError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the system error looks like" (blueprint)
    - Exception classes = "WHEN the system error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import SysErrorDefinition


class UnknownError(SysErrorDefinition):
    """Error definition for unexpected system errors.

    This error occurs when an unexpected system error happens that
    doesn't fall into any specific error category. It serves as
    a catch-all for unhandled exceptions.

    Attributes:
        code: SYS_UNKNOWN_ERROR
        http_status: 500 Internal Server Error
        message_template: "Unexpected error. Reference: {reference_id}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in a system-specific exception
        ... raise SystemError(UnknownError(reference_id="ERR-12345"))
    """

    code = "SYS_UNKNOWN_ERROR"
    http_status = 500
    message_template = _n("Unexpected error. Reference: {reference_id}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an unknown system error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InternalError(SysErrorDefinition):
    """Error definition for internal server errors.

    This error occurs when the server encounters an internal error
    that prevents it from fulfilling the request. This typically
    indicates a bug or misconfiguration in the application.

    Attributes:
        code: SYS_INTERNAL_ERROR
        http_status: 500 Internal Server Error
        message_template: "Internal server error. Reference: {reference_id}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in a system-specific exception
        ... raise SystemError(InternalError(reference_id="INT-12345"))
    """

    code = "SYS_INTERNAL_ERROR"
    http_status = 500
    message_template = _n("Internal server error. Reference: {reference_id}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an internal server error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ServiceUnavailable(SysErrorDefinition):
    """Error definition for service unavailability.

    This error occurs when the service is temporarily unavailable
    due to maintenance, overload, or other operational issues.
    The operation can be retried later.

    Attributes:
        code: SYS_SERVICE_UNAVAILABLE
        http_status: 503 Service Unavailable
        message_template: "Service temporarily unavailable. Please try again later."
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in a system-specific exception
        ... raise SystemError(ServiceUnavailable())
    """

    code = "SYS_SERVICE_UNAVAILABLE"
    http_status = 503
    message_template = _n("Service temporarily unavailable. Please try again later.")
    is_retryable = True


class Timeout(SysErrorDefinition):
    """Error definition for system timeout errors.

    This error occurs when a system operation exceeds the maximum
    allowed execution time. The operation can be retried with a
    smaller request or later.

    Attributes:
        code: SYS_TIMEOUT
        http_status: 504 Gateway Timeout
        message_template: "Request timeout. Please try again with smaller request or later."
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in a system-specific exception
        ... raise SystemError(Timeout())
    """

    code = "SYS_TIMEOUT"
    http_status = 504
    message_template = _n(
        "Request timeout. Please try again with smaller request or later."
    )
    is_retryable = True


class UserCreationFailed(SysErrorDefinition):
    """Error definition for user creation failures.

    This error occurs when the system fails to create a new user
    due to internal errors, data inconsistencies, or system constraints.

    Attributes:
        code: SYS_USER_CREATION_FAILED
        http_status: 500 Internal Server Error
        message_template: "Failed to create user: {error_detail}"
        is_retryable: True (retrying may succeed after fixing issue)

    Example:
        >>> # Wrap this definition in a system-specific exception
        ... raise SystemError(UserCreationFailed(
        ...     error_detail="Username generation failed"
        ... ))
    """

    code = "SYS_USER_CREATION_FAILED"
    http_status = 500
    message_template = _n("Failed to create user: {error_detail}")
    is_retryable = True

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        error_detail: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a user creation failed error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
