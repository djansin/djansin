"""Provides application-level exception classes for common app-related issues.

This module defines concrete exception classes that wrap application error
definitions. Each exception corresponds to a specific application error scenario
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY an application error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the application error looks like" (blueprint)
    - Exception classes (here) = "WHEN the application error happens" (raised in code flow)
"""

from typing import Any, overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import AppError
from core.exceptions.errors.app import (
    AttributeNotFound,
    InvalidFormat,
    InvalidHalfYear,
    InvalidSeason,
    InvalidUsername,
    InvalidValue,
    RequiredField,
)
from core.exceptions.errors.common import AppErrorDefinition


class RequiredFieldError(AppError):
    """Raised when a required field is missing from the input data.

    This exception is raised when a required field is not provided in the
    submitted data.

    Common scenarios:
    - Missing 'email' field in registration form
    - Missing 'username' field in login request
    - Missing required query parameter in API request

    This error is NOT retryable as the client must provide the field.

    Attributes:
        _error_cls: The RequiredField error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = RequiredField
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        field: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes a required field validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidFormatError(AppError):
    """Raised when a value does not match the expected format.

    This exception is raised when a field value does not conform to an
    expected format pattern (UUID, date, time, etc.).

    Common scenarios:
    - Invalid UUID format
    - Incorrect date format (expected YYYY-MM-DD)
    - Invalid time format
    - Invalid URL format

    This error is NOT retryable as the client must provide correct format.

    Attributes:
        _error_cls: The InvalidFormat error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = InvalidFormat
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        expected_format: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid format validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidSeasonError(AppError):
    """Raised when a season value is invalid.

    This exception is raised when a season number is not between 1 and 4
    (representing Spring, Summer, Autumn, Winter).

    Common scenarios:
    - Invalid season number in filter
    - Season parameter out of valid range
    - Season value not an integer
    - Non-existent season requested

    This error is NOT retryable as the client must provide valid season.

    Attributes:
        _error_cls: The InvalidSeason error definition class.
        severity: INFO - normal parameter issues.
    """

    _error_cls = InvalidSeason
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        season: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid season validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidHalfYearError(AppError):
    """Raised when a half-year value is invalid.

    This exception is raised when a half-year number is not 1 or 2
    (representing First Half and Second Half of the year).

    Common scenarios:
    - Invalid half-year in fiscal reports
    - Half-year parameter out of valid range
    - Half-year value not an integer
    - Non-existent half-year requested

    This error is NOT retryable as the client must provide valid half-year.

    Attributes:
        _error_cls: The InvalidHalfYear error definition class.
        severity: INFO - normal parameter issues.
    """

    _error_cls = InvalidHalfYear
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        half: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid half-year validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class UsernameValidationError(AppError):
    """Raised when username validation fails.

    This exception is raised when a username does not meet validation
    requirements. It supports structured error details for both field-specific
    and non-field errors.

    Common scenarios:
    - Username contains invalid characters
    - Username already exists
    - Username is too short or too long
    - Username is on reserved words list
    - Username format validation fails

    This error is NOT retryable as the client must choose a valid username.

    Attributes:
        _error_cls: The InvalidUsername error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = InvalidUsername
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        field_errors: dict[str, list[str]] | None = None,
        non_field_errors: list[str] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes a username validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class AttributeNotFoundError(AppError):
    """Raised when an attribute is accessed that does not exist on an object.

    This exception is raised when application code attempts to access an
    attribute that doesn't exist on an object. This indicates a programming
    error where the code assumes an attribute that the object doesn't have.

    Common scenarios:
    - Accessing a field that doesn't exist on a model instance
    - Dictionary key lookup failure for missing key
    - Object attribute access for non-existent attribute
    - Missing method or property on an object

    This error is NOT retryable as it requires code correction.

    Attributes:
        _error_cls: The AttributeNotFound error definition class.
        severity: ERROR - indicates a programming error that needs attention.
    """

    _error_cls = AttributeNotFound
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        object_type: str | None = None,
        attribute_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes an attribute not found exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidValueError(AppError):
    """Raised when a value is invalid for the expected type or domain.

    This exception is raised when a value does not meet the expected
    requirements, constraints, or type for a field or parameter. This is a
    generic error for value validation failures that don't fit more specific
    categories.

    Common scenarios:
    - Invalid type passed to a function
    - Value outside expected range or domain
    - Value with invalid format or structure
    - Incompatible value for operation

    This error is NOT retryable as it requires correcting the value.

    Attributes:
        _error_cls: The InvalidValue error definition class.
        severity: ERROR - indicates a programming error or invalid data.
    """

    _error_cls = InvalidValue
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | AppErrorDefinition | None = None,
        /,
        *,
        value: Any | None = None,
    ) -> None: ...

    def __init__(self, error: str | AppErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid value exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
