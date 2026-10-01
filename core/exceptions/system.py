"""Provides system-level exception classes for internal infrastructure issues.

This module defines concrete exception classes that wrap system error
definitions. Each exception corresponds to a specific system error scenario
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY a system error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the system error looks like" (blueprint)
    - Exception classes (here) = "WHEN the system error happens" (raised in code flow)
"""

from typing import overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import SystemError
from core.exceptions.errors.common import SysErrorDefinition
from core.exceptions.errors.system import (
    InternalError,
    ServiceUnavailable,
    Timeout,
    UnknownError,
    UserCreationFailed,
)


class UnknownSystemError(SystemError):
    """Raised when an unexpected system error occurs without specific classification.

    This exception is raised as a catch-all for unclassified system failures
    when no more specific error category applies.

    Common scenarios:
    - Unhandled exception in unexpected code path
    - Generic system error without specific cause
    - Third-party library raises unknown error
    - Resource exhaustion without specific type

    This error is NOT retryable as it requires investigation.

    Attributes:
        _error_cls: The UnknownError error definition class.
        severity: ERROR - unknown errors need investigation.
    """

    _error_cls = UnknownError
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | SysErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | SysErrorDefinition | None = None, /, **kwds):
        """Initializes an unknown system error exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InternalServerError(SystemError):
    """Raised when an internal server error occurs.

    This exception is raised for internal server failures such as unhandled
    exceptions or unexpected conditions in server-side code.

    Common scenarios:
    - Unhandled exception in view or service layer
    - Configuration error causing server failure
    - Resource leak or exhaustion
    - Programming error (null pointer, assertion failure)
    - Third-party library internal failure

    This error is NOT retryable as it requires code investigation.

    Attributes:
        _error_cls: The InternalError error definition class.
        severity: ERROR - internal server errors need immediate attention.
    """

    _error_cls = InternalError
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | SysErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | SysErrorDefinition | None = None, /, **kwds):
        """Initializes an internal server error exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class ServiceUnavailableError(SystemError):
    """Raised when a service is temporarily unavailable.

    This exception is raised when the service cannot handle requests due to
    overload, maintenance, or dependency failures.

    Common scenarios:
    - Database connection pool exhausted
    - Cache service unavailable
    - Message queue backlog or downtime
    - Application under heavy load
    - Scheduled maintenance in progress

    This error IS retryable as the service may recover.

    Attributes:
        _error_cls: The ServiceUnavailable error definition class.
        severity: ERROR - service unavailability affects all users.
    """

    _error_cls = ServiceUnavailable
    severity = ExceptionSeverity.ERROR


class SystemTimeoutError(SystemError):
    """Raised when a system-wide timeout condition occurs.

    This exception is raised when a system-wide operation exceeds its allowed
    execution time, such as request processing or background jobs.

    Common scenarios:
    - HTTP request processing timeout
    - Background task exceeds time limit
    - Long-running database query timeout
    - File upload processing timeout
    - Batch job execution timeout

    This error IS retryable as retry with smaller request may succeed.

    Attributes:
        _error_cls: The Timeout error definition class.
        severity: ERROR - timeouts indicate performance issues.
    """

    _error_cls = Timeout
    severity = ExceptionSeverity.ERROR


class UserCreationFailedError(SystemError):
    """Raised when user creation fails due to system issues.

    This exception is raised for user creation failures that are not related
    to validation or business rules, such as infrastructure issues.

    Common scenarios:
    - Database connection failure during user creation
    - Email notification service unavailable
    - Profile creation fails in external service
    - Transaction rollback due to system error
    - Storage quota exceeded for user data

    This error IS retryable as retry may succeed after system recovery.

    Attributes:
        _error_cls: The UserCreationFailed error definition class.
        severity: ERROR - user creation failures affect onboarding.
    """

    _error_cls = UserCreationFailed
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | SysErrorDefinition | None = None,
        /,
        *,
        error_detail: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | SysErrorDefinition | None = None, /, **kwds):
        """Initializes a user creation failed exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
