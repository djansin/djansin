"""Provides validation exception classes for data validation failures.

This module defines concrete exception classes that wrap validation error
definitions. Each exception corresponds to a specific validation error scenario
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY a validation error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the validation error looks like" (blueprint)
    - Exception classes (here) = "WHEN the validation error happens" (raised in code flow)
"""

from typing import Any, overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import ValidationError
from core.exceptions.errors.common import ValidErrorDefinition
from core.exceptions.errors.validation import (
    CredentialsRequired,
    FieldTooLong,
    FieldTooShort,
    InvalidEmail,
    InvalidFormat,
    InvalidHalfYear,
    InvalidPhone,
    InvalidRange,
    InvalidSeason,
    InvalidUsername,
    PasswordConfirmationMismatch,
    PatternMismatch,
    RequiredField,
)


class RequiredFieldError(ValidationError):
    """Raised when a required field is missing.

    This exception is raised when a required field is not provided in the
    input data.

    Common scenarios:
    - Missing 'email' field in registration form
    - Missing 'username' field in login request
    - Missing 'password' field in password reset form
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
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        field: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes a required field validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidEmailError(ValidationError):
    """Raised when an email address has invalid format.

    This exception is raised when an email address does not conform to valid
    email format standards.

    Common scenarios:
    - Missing '@' symbol in email
    - Invalid domain format
    - Consecutive dots in local part
    - Invalid characters in email address

    This error is NOT retryable as the client must provide a valid email.

    Attributes:
        _error_cls: The InvalidEmail error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = InvalidEmail
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        email: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid email validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidPhoneError(ValidationError):
    """Raised when a phone number has invalid format.

    This exception is raised when a phone number does not conform to valid
    phone number format standards for the expected region.

    Common scenarios:
    - Incorrect number of digits
    - Invalid country code
    - Invalid characters in phone number
    - Missing required area code

    This error is NOT retryable as the client must provide a valid phone number.

    Attributes:
        _error_cls: The InvalidPhone error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = InvalidPhone
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        phone: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid phone number validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class FieldTooLongError(ValidationError):
    """Raised when a field value exceeds maximum length.

    This exception is raised when a string field value has more characters
    than the allowed maximum length.

    Common scenarios:
    - Username exceeds maximum character limit
    - Description field too long for database column
    - Input exceeds form field maxlength attribute
    - Text exceeds storage limit

    This error is NOT retryable as the client must shorten the value.

    Attributes:
        _error_cls: The FieldTooLong error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = FieldTooLong
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        field: str | None = None,
        max_length: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes a field too long validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class FieldTooShortError(ValidationError):
    """Raised when a field value is below minimum length.

    This exception is raised when a string field value has fewer characters
    than the required minimum length.

    Common scenarios:
    - Password shorter than minimum length requirement
    - Username too short
    - Input doesn't meet minimum character requirement
    - Search query too short for searching

    This error is NOT retryable as the client must provide a longer value.

    Attributes:
        _error_cls: The FieldTooShort error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = FieldTooShort
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        field: str | None = None,
        min_length: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes a field too short validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidFormatError(ValidationError):
    """Raised when a value does not match expected format.

    This exception is raised when a value does not conform to an expected
    format pattern (UUID, date, time, etc.).

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
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        expected_format: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid format validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidRangeError(ValidationError):
    """Raised when a value is outside allowed range.

    This exception is raised when a numeric value is less than minimum or
    greater than maximum allowed value.

    Common scenarios:
    - Age outside allowed range (e.g., 0-120)
    - Rating value not between 1 and 5
    - Price not within allowed range
    - Percentage value not between 0 and 100

    This error is NOT retryable as the client must provide a valid value.

    Attributes:
        _error_cls: The InvalidRange error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = InvalidRange
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        min_value: Any | None = None,
        max_value: Any | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid range validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class PatternMismatchError(ValidationError):
    """Raised when a value does not match required regex pattern.

    This exception is raised when a string value does not conform to the
    required regular expression pattern.

    Common scenarios:
    - Invalid slug format (only letters, numbers, hyphens)
    - Invalid license plate format
    - Invalid postal code format
    - Invalid hexadecimal color code

    This error is NOT retryable as the client must provide a matching value.

    Attributes:
        _error_cls: The PatternMismatch error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = PatternMismatch
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        pattern: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes a pattern mismatch validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class UsernameValidationError(ValidationError):
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
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        field_errors: dict[str, list[str]] | None = None,
        non_field_errors: list[str] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes a username validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class PasswordConfirmationMismatchError(ValidationError):
    """Raised when password and confirmation do not match.

    This exception is raised when the password confirmation field does not
    match the original password field.

    Common scenarios:
    - Password reset with mismatched confirmation
    - Registration form with different passwords
    - Change password form with mismatch
    - Account setup with confirmation error

    This error is NOT retryable as the client must provide matching passwords.

    Attributes:
        _error_cls: The PasswordConfirmationMismatch error definition class.
        severity: INFO - normal user input issues.
    """

    _error_cls = PasswordConfirmationMismatch
    severity = ExceptionSeverity.INFO


class CredentialsRequiredError(ValidationError):
    """Raised when authentication credentials are missing.

    This exception is raised when both identifier and password are required
    for authentication but one or both are missing.

    Common scenarios:
    - Login request missing username/email
    - Authentication endpoint missing password
    - Missing credentials for token refresh
    - Incomplete authentication payload

    This error is NOT retryable as the client must provide both fields.

    Attributes:
        _error_cls: The CredentialsRequired error definition class.
        severity: INFO - normal client issues.
    """

    _error_cls = CredentialsRequired
    severity = ExceptionSeverity.INFO


class InvalidSeasonError(ValidationError):
    """Raised when season value is invalid.

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
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        season: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid season validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class InvalidHalfYearError(ValidationError):
    """Raised when half-year value is invalid.

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
        error: str | ValidErrorDefinition | None = None,
        /,
        *,
        half: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ValidErrorDefinition | None = None, /, **kwds):
        """Initializes an invalid half-year validation exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
