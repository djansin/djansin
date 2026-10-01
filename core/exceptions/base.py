"""Provides base exception classes for the application's error handling system.

This module defines foundational exception classes that bridge the gap between
error definitions (blueprints) and runtime exceptions. It includes severity
levels for errors and base exception classes that work with ErrorDefinition
instances to provide consistent error handling across the application.

IMPORTANT - What these classes represent:
    - ExceptionSeverity: Classification of error severity for monitoring and response
    - BaseAppException: Bridge between ErrorDefinition and runtime exceptions
    - Each exception wraps an ErrorDefinition to provide structured error information

Key distinction:
    - ErrorDefinition classes = "WHAT the error looks like" (blueprint)
    - BaseAppException classes = "WHEN the error happens" (raised in code flow)
    - Severity levels = "HOW IMPORTANT the error is" (monitoring priority)
"""

from enum import Enum, auto
from typing import Any, ClassVar, Generic, TypeVar

from core.exceptions.errors.base import ErrorDefinition


class ExceptionSeverity(Enum):
    """Enumeration of error severity levels for exception classification.

    This enum defines severity levels that can be assigned to exceptions,
    helping to determine appropriate responses, monitoring, and alerting
    strategies based on error criticality.

    Attributes:
        DEBUG: Development/debugging information, not typically surfaced to users.
        INFO: Informational messages about normal operation.
        WARNING: Non-critical issues that may require attention.
        ERROR: Errors that affect functionality but not system stability.
        CRITICAL: Severe errors that require immediate attention.
        FATAL: Catastrophic errors requiring service termination.

    Properties:
        requires_admin_panel: True for ERROR, CRITICAL, and FATAL severity.
        requires_contact_admin: True for CRITICAL and FATAL severity.
        requires_service_stop: True only for FATAL severity.
    """

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    FATAL = auto()

    @property
    def requires_admin_panel(self) -> bool:
        """Indicates if the error should be displayed in the admin panel.

        Returns:
            True for ERROR, CRITICAL, and FATAL severity levels.
        """
        return self in {self.ERROR, self.CRITICAL, self.FATAL}

    @property
    def requires_contact_admin(self) -> bool:
        """Indicates if the user should be prompted to contact an admin.

        Returns:
            True for CRITICAL and FATAL severity levels.
        """
        return self in {self.CRITICAL, self.FATAL}

    @property
    def requires_service_stop(self) -> bool:
        """Indicates if the service should be stopped.

        Returns:
            True only for FATAL severity level.
        """
        return self is self.FATAL


ErrorDefinitionType = TypeVar("ErrorDefinitionType", bound="ErrorDefinition")


class BaseAppException(Exception, Generic[ErrorDefinitionType]):
    """Base exception class that wraps ErrorDefinition instances.

    This class serves as the foundation for all application exceptions,
    providing a consistent interface for accessing error information
    and maintaining compatibility with the error definition system.

    Class Attributes:
        _error_cls: The ErrorDefinition class associated with this exception.
        severity: The default severity level for this exception type.

    Attributes:
        _error: The wrapped ErrorDefinition instance.
        _severity: The severity level for this specific exception instance.

    Example:
        >>> # Define a custom exception
        ... class BusinessError(BaseAppException):
        ...     _error_cls = BizErrorDefinition
        ...     severity = ExceptionSeverity.ERROR

        >>> # Raise with an error definition
        ... raise BusinessError(InsufficientFunds(required=100.0, available=50.0))
    """

    _error_cls: ClassVar[type[ErrorDefinitionType]]
    severity: ClassVar[ExceptionSeverity]

    def __init__(
        self,
        error: str | ErrorDefinitionType | None = None,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _details: dict[str, Any] | None = None,
        _severity: ExceptionSeverity | None = None,
        **context,
    ) -> None:
        """Initializes a BaseAppException instance.

        Args:
            error: Either an ErrorDefinition instance, a message template string,
                or None. If a string or None is provided, creates an instance
                using the class's _error_cls.
            _code: Optional custom error code override.
            _http_status: Optional custom HTTP status code override.
            _is_retryable: Optional custom retryability flag override.
            _details: Optional structured details dictionary.
            _severity: Optional custom severity level override.
            **context: Context values for message formatting.

        Example:
            >>> # Using an error definition
            ... raise BusinessError(InsufficientFunds(required=100.0, available=50.0))

            >>> # Using a message template string
            ... raise BusinessError("Custom message with {context}", key="value")

            >>> # With overrides
            ... raise BusinessError(
            ...     InsufficientFunds(required=100.0, available=50.0),
            ...     _code="CUSTOM_CODE",
            ...     _http_status=400
            ... )
        """
        if isinstance(error, str) or error is None:
            error_cls = self.__class__._error_cls
            error = error_cls(error, **context)

        self._error = error.derive(
            _code=_code,
            _http_status=_http_status,
            _is_retryable=_is_retryable,
            _details=_details,
        )
        self._severity = _severity

        super().__init__(f"[{self.severity.name}] {self.code}: {error.message}")

    @property
    def error(self) -> ErrorDefinitionType:
        """Returns the wrapped ErrorDefinition instance.

        Returns:
            The ErrorDefinition instance containing the error details.
        """
        return self._error

    @property
    def message(self) -> str:
        """Returns the formatted error message in English.

        Returns:
            The formatted message string in English.
        """
        return self.error.message

    @property
    def user_message(self):
        """Returns the formatted error message in the active language.

        Returns:
            The formatted message string in the active language.
        """
        return self.error.user_message

    @property
    def code(self) -> str:
        """Returns the error code.

        Returns:
            The error code string.
        """
        return self.error.code

    @property
    def http_status(self) -> int:
        """Returns the HTTP status code.

        Returns:
            The HTTP status code integer.
        """
        return self.error.http_status

    @property
    def is_retryable(self) -> bool:
        """Indicates if the operation can be retried.

        Returns:
            True if the operation can be retried, False otherwise.
        """
        return self.error.is_retryable

    @property
    def severity(self) -> ExceptionSeverity:
        """Returns the exception severity level.

        Returns:
            The severity level for this exception instance.
            Uses instance-specific severity if set, otherwise the class default.
        """
        return self.__class__.severity if self._severity is None else self._severity

    @property
    def context(self) -> dict[str, Any]:
        """Returns the context dictionary for message formatting.

        Returns:
            The dictionary of context values used for message formatting.
        """
        return self.error.context

    @property
    def details(self) -> dict[str, Any]:
        """Returns the structured details for the error.

        Returns:
            The structured details dictionary.
        """
        return self.error.details

    def to_dict(self) -> dict[str, Any]:
        """Converts the exception to a dictionary representation.

        Returns:
            A dictionary containing the error code, HTTP status, user message,
            retryability flag, and structured details.

        Example:
            >>> try:
            ...     raise BusinessError(InsufficientFunds(required=100.0, available=50.0))
            ... except BusinessError as e:
            ...     print(e.to_dict())
        """
        return self.error.to_dict()
