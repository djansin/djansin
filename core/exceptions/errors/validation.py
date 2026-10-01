"""Provides validation error definitions for data validation failures.

This module defines concrete error definition classes for validation-related
errors including required fields, invalid formats, length violations, pattern
mismatches, range violations, file upload errors, and domain-specific
validations like seasons, half-years, and trust levels.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a validation error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like ValidationError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the validation error looks like" (blueprint)
    - Exception classes = "WHEN the validation error happens" (raised in code flow)
"""

from typing import Any, overload

from django.utils.translation import gettext_lazy as _t, gettext_noop as _n

from core.exceptions.errors.common import ValidErrorDefinition


class RequiredField(ValidErrorDefinition):
    """Error definition for missing required fields.

    This error occurs when a required field is missing from the
    submitted data.

    Attributes:
        code: VALID_REQUIRED_FIELD
        http_status: 422 Unprocessable Entity
        message_template: "Field '{field}' is required."
        is_retryable: False (requires field value)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(RequiredField(field="email"))
    """

    code = "VALID_REQUIRED_FIELD"
    http_status = 422
    message_template = _n("Field '{field}' is required.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a required field validation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidEmail(ValidErrorDefinition):
    """Error definition for invalid email addresses.

    This error occurs when a provided email address does not meet
    the required format or validation rules.

    Attributes:
        code: VALID_INVALID_EMAIL
        http_status: 422 Unprocessable Entity
        message_template: "Email '{email}' is not valid."
        is_retryable: False (requires valid email)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidEmail(email="invalid@"))
    """

    code = "VALID_INVALID_EMAIL"
    http_status = 422
    message_template = _n("Email '{email}' is not valid.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        email: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid email error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidPhone(ValidErrorDefinition):
    """Error definition for invalid phone numbers.

    This error occurs when a provided phone number does not meet
    the required format or validation rules.

    Attributes:
        code: VALID_INVALID_PHONE
        http_status: 422 Unprocessable Entity
        message_template: "Phone number '{number}' is not valid."
        is_retryable: False (requires valid phone number)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidPhone(number="123456"))
    """

    code = "VALID_INVALID_PHONE"
    http_status = 422
    message_template = _n("Phone number '{number}' is not valid.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        number: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid phone number error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class FieldTooLong(ValidErrorDefinition):
    """Error definition for fields exceeding maximum length.

    This error occurs when a field value exceeds the maximum
    allowed character length.

    Attributes:
        code: VALID_FIELD_TOO_LONG
        http_status: 422 Unprocessable Entity
        message_template: "Field '{field}' must not exceed {max_length} characters."
        is_retryable: False (requires shorter value)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(FieldTooLong(field="title", max_length=100))
    """

    code = "VALID_FIELD_TOO_LONG"
    http_status = 422
    message_template = _n("Field '{field}' must not exceed {max_length} characters.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field: str | None = None,
        max_length: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a field too long validation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class FieldTooShort(ValidErrorDefinition):
    """Error definition for fields below minimum length.

    This error occurs when a field value is shorter than the
    minimum required character length.

    Attributes:
        code: VALID_FIELD_TOO_SHORT
        http_status: 422 Unprocessable Entity
        message_template: "Field '{field}' must be at least {min_length} characters."
        is_retryable: False (requires longer value)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(FieldTooShort(field="password", min_length=8))
    """

    code = "VALID_FIELD_TOO_SHORT"
    http_status = 422
    message_template = _n("Field '{field}' must be at least {min_length} characters.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field: str | None = None,
        min_length: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a field too short validation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidFormat(ValidErrorDefinition):
    """Error definition for invalid data format.

    This error occurs when a field value does not match the
    expected data format or pattern.

    Attributes:
        code: VALID_INVALID_FORMAT
        http_status: 422 Unprocessable Entity
        message_template: "Invalid format. Expected {expected_format}."
        is_retryable: False (requires correct format)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidFormat(expected_format="YYYY-MM-DD"))
    """

    code = "VALID_INVALID_FORMAT"
    http_status = 422
    message_template = _n("Invalid format. Expected {expected_format}.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        expected_format: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid format error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidRange(ValidErrorDefinition):
    """Error definition for values outside allowed range.

    This error occurs when a numeric value falls outside the
    minimum and maximum allowed range.

    Attributes:
        code: VALID_INVALID_RANGE
        http_status: 422 Unprocessable Entity
        message_template: "Value must be between {min_value} and {max_value}."
        is_retryable: False (requires value within range)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidRange(min_value=1, max_value=100))
    """

    code = "VALID_INVALID_RANGE"
    http_status = 422
    message_template = _n("Value must be between {min_value} and {max_value}.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        min_value: Any | None = None,
        max_value: Any | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid range error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class PatternMismatch(ValidErrorDefinition):
    """Error definition for regex pattern validation failures.

    This error occurs when a field value does not match the
    required regular expression pattern.

    Attributes:
        code: VALID_PATTERN_MISMATCH
        http_status: 422 Unprocessable Entity
        message_template: "Value does not match required pattern: {pattern}."
        is_retryable: False (requires pattern match)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(PatternMismatch(pattern="^[A-Z]+$"))
    """

    code = "VALID_PATTERN_MISMATCH"
    http_status = 422
    message_template = _n("Value does not match required pattern: {pattern}.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        pattern: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a pattern mismatch error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidUsername(ValidErrorDefinition):
    """Error definition for username validation failures.

    This error occurs when a username fails validation rules
    including format, length, or uniqueness constraints.

    Attributes:
        code: VALID_INVALID_USERNAME
        http_status: 422 Unprocessable Entity
        message_template: "Validation failed. Please check the provided data."
        is_retryable: False (requires valid username)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidUsername(
        ...     field_errors={"username": ["Must be at least 3 characters"]}
        ... ))
    """

    code = "VALID_INVALID_USERNAME"
    http_status = 422
    message_template = _n("Validation failed. Please check the provided data.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field_errors: dict[str, list[str]] | None = None,
        non_field_errors: list[str] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a username validation error definition.

        Passes all arguments to the parent class constructor.
        """
        self.field_errors = kwds.get("field_errors", {})
        self.non_field_errors = kwds.get("non_field_errors", [])
        super().__init__(message_template, **kwds)

    @property
    def get_details(self) -> dict[str, dict[str, list[str]] | list[str]]:
        """Returns structured validation error details.

        Returns:
            dict: A dictionary containing field_errors and non_field_errors
                for structured error responses.
        """
        return {
            "field_errors": self.field_errors,
            "non_field_errors": self.non_field_errors,
        }


class PasswordConfirmationMismatch(ValidErrorDefinition):
    """Error definition for password confirmation failures.

    This error occurs when the password and password confirmation
    fields do not match.

    Attributes:
        code: VALID_PASSWORD_CONFIRMATION_MISMATCH
        http_status: 422 Unprocessable Entity
        message_template: "Password confirmation does not match."
        is_retryable: False (requires matching password)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(PasswordConfirmationMismatch())
    """

    code = "VALID_PASSWORD_CONFIRMATION_MISMATCH"
    http_status = 422
    message_template = _n("Password confirmation does not match.")
    is_retryable = False


class CredentialsRequired(ValidErrorDefinition):
    """Error definition for missing authentication credentials.

    This error occurs when both identifier and password are not
    provided for authentication.

    Attributes:
        code: VALID_CREDENTIALS_REQUIRED
        http_status: 422 Unprocessable Entity
        message_template: "Both identifier and password are required for authentication."
        is_retryable: False (requires credentials)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(CredentialsRequired())
    """

    code = "VALID_CREDENTIALS_REQUIRED"
    http_status = 422
    message_template = _n(
        "Both identifier and password are required for authentication."
    )
    is_retryable = False


class InvalidSeason(ValidErrorDefinition):
    """Error definition for invalid season numbers.

    This error occurs when a season number is outside the valid
    range of 1 to 4.

    Attributes:
        code: VALID_INVALID_SEASON
        http_status: 422 Unprocessable Entity
        message_template: "Invalid season: {season}. Must be between 1 and 4."
        is_retryable: False (requires valid season)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidSeason(season=5))
    """

    code = "VALID_INVALID_SEASON"
    http_status = 422
    message_template = _n("Invalid season: {season}. Must be between 1 and 4.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        season: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid season error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidHalfYear(ValidErrorDefinition):
    """Error definition for invalid half-year numbers.

    This error occurs when a half-year number is outside the
    valid range of 1 or 2.

    Attributes:
        code: VALID_INVALID_HALF_YEAR
        http_status: 422 Unprocessable Entity
        message_template: "Invalid half-year number: {half}. Must be 1 or 2."
        is_retryable: False (requires valid half-year)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidHalfYear(half=3))
    """

    code = "VALID_INVALID_HALF_YEAR"
    http_status = 422
    message_template = _n("Invalid half-year number: {half}. Must be 1 or 2.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        half: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid half-year error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Validation(ValidErrorDefinition):
    """Error definition for comprehensive validation failures.

    This error occurs when multiple validation errors are detected
    across various fields in the submitted data.

    Attributes:
        code: VALID_VALIDATION_ERROR
        http_status: 422 Unprocessable Entity
        message_template: "Validation failed. {detail}"
        is_retryable: False (requires data correction)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(Validation(
        ...     field_errors={"email": ["Invalid format"]},
        ...     non_field_errors=["Data mismatch"],
        ...     detail="Please correct the highlighted fields"
        ... ))
    """

    code = "VALID_VALIDATION_ERROR"
    http_status = 422
    message_template = _n("Validation failed. {detail}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field_errors: dict[str, list[str]] | None = None,
        non_field_errors: list[str] | None = None,
        detail: str = _t("Please check your input."),
        **kwds,
    ) -> None: ...

    def __init__(
        self,
        message_template: str | None = None,
        /,
        detail: str = _t("Please check your input."),
        **kwds,
    ):
        """Initializes a validation error definition.

        Passes all arguments to the parent class constructor.
        """
        self._field_errors = kwds.get("field_errors", {})
        self._non_field_errors = kwds.get("non_field_errors", [])
        super().__init__(message_template, detail=detail, **kwds)

    @property
    def details(self) -> dict[str, dict | list]:
        """Returns structured validation error details.

        Returns:
            dict: A dictionary containing field_errors and non_field_errors.
        """
        return {
            "field_errors": self._field_errors,
            "non_field_errors": self._non_field_errors,
        }


class UploadedFileError(ValidErrorDefinition):
    """Error definition for file upload failures.

    This error occurs when a file upload fails validation due to
    size limits, type restrictions, or other file-related constraints.

    Attributes:
        code: VALID_UPLOAD_ERROR
        http_status: 400 Bad Request
        message_template: "File upload error: {detail}"
        is_retryable: False (requires file correction)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(UploadedFileError(
        ...     detail="File size exceeds 5MB limit"
        ... ))
    """

    code = "VALID_UPLOAD_ERROR"
    http_status = 400
    message_template = _n("File upload error: {detail}")
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
        """Initializes an uploaded file error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidTrustLevel(ValidErrorDefinition):
    """Error definition for invalid trust level values.

    This error occurs when a provided trust level value is not one of the
    allowed trust level values defined in the system.

    Attributes:
        code: VALID_INVALID_TRUST_LEVEL
        http_status: 422 Unprocessable Entity
        message_template: "Invalid trust level: {new_level}. Must be one of {allowed_levels}."
        is_retryable: False (requires valid trust level value)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise ValidationError(InvalidTrustLevel(
        ...     new_level="super_admin",
        ...     allowed_levels=["admin", "user", "guest"]
        ... ))
    """

    code = "VALID_INVALID_TRUST_LEVEL"
    http_status = 422
    message_template = _n(
        "Invalid trust level: {new_level}. Must be one of {allowed_levels}."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        new_level: str | int | None = None,
        allowed_levels: list[str] | list[int] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid trust level error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
