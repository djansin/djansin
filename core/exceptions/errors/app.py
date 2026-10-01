"""Provides application-level error definitions for common app-related issues.

This module defines concrete error definition classes for application-level
errors including model field validation, aggregation type validation, field
requirements, format validation, and domain-specific validations like seasons,
half-years, usernames, and trust levels.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW an application error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like AppError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the application error looks like" (blueprint)
    - Exception classes = "WHEN the application error happens" (raised in code flow)
"""

from typing import Any, overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import AppErrorDefinition


class ModelFieldNotFound(AppErrorDefinition):
    """Error definition for referenced fields that do not exist on a model.

    This error occurs at the application level when an operation references a
    field name that does not exist on the specified model. This indicates a
    programming error in the application code where a model field is being
    accessed that doesn't exist.

    Attributes:
        code: "APP:MODEL_FIELD_NOT_FOUND"
        http_status: 500 Internal Server Error
        message_template: "Field '{field_name}' does not exist on model '{model_name}'."
        is_retryable: False (requires code correction)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(ModelFieldNotFound(
        ...     field_name="non_existent_field",
        ...     model_name="User"
        ... ))
    """

    code = "APP:MODEL_FIELD_NOT_FOUND"
    http_status = 500
    message_template = _n(
        "Field '{field_name}' does not exist on model '{model_name}'."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        field_name: str | None = None,
        model_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a model field not found error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class UnsupportedAggregationType(AppErrorDefinition):
    """Error definition for unsupported aggregation types.

    This error occurs at the application level when a specified aggregation
    type is not supported by the system. This indicates a logical error in
    the application code where an unsupported aggregation type is being used.

    Attributes:
        code: "APP:UNSUPPORTED_AGGREGATION_TYPE"
        http_status: 500 Internal Server Error
        message_template: "Unsupported aggregation type: '{agg_type}'."
        is_retryable: False (requires using a supported aggregation type)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(UnsupportedAggregationType(agg_type="custom_agg"))
    """

    code = "APP:UNSUPPORTED_AGGREGATION_TYPE"
    http_status = 500
    message_template = _n("Unsupported aggregation type: '{agg_type}'.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        agg_type: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an unsupported aggregation type error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class RequiredField(AppErrorDefinition):
    """Error definition for missing required fields in application operations.

    This error occurs at the application level when a required field is missing
    from the data being processed. This indicates that the application logic
    expected a field that wasn't provided, which could be due to a programming
    error or missing data.

    Attributes:
        code: "APP:REQUIRED_FIELD"
        http_status: 500 Internal Server Error
        message_template: "Field '{field}' is required."
        is_retryable: False (requires field value)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(RequiredField(field="email"))
    """

    code = "APP:REQUIRED_FIELD"
    http_status = 500
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
        """Initializes a required field error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidFormat(AppErrorDefinition):
    """Error definition for invalid format in application data.

    This error occurs at the application level when data doesn't match the
    expected format. This indicates a mismatch in data format expectations
    within the application logic.

    Attributes:
        code: "APP:INVALID_FORMAT"
        http_status: 500 Internal Server Error
        message_template: "Invalid format. Expected {expected_format}."
        is_retryable: False (requires correct format)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidFormat(expected_format="YYYY-MM-DD"))
    """

    code = "APP:INVALID_FORMAT"
    http_status = 500
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


class InvalidSeason(AppErrorDefinition):
    """Error definition for invalid season numbers in application logic.

    This error occurs at the application level when a season number is outside
    the valid range of 1 to 4. This indicates a logical error in the application
    where an invalid season value is being processed.

    Attributes:
        code: "APP:INVALID_SEASON"
        http_status: 500 Internal Server Error
        message_template: "Invalid season: {season}. Must be between 1 and 4."
        is_retryable: False (requires valid season)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidSeason(season=5))
    """

    code = "APP:INVALID_SEASON"
    http_status = 500
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


class InvalidHalfYear(AppErrorDefinition):
    """Error definition for invalid half-year numbers in application logic.

    This error occurs at the application level when a half-year number is
    outside the valid range of 1 or 2. This indicates a logical error in the
    application where an invalid half-year value is being processed.

    Attributes:
        code: "APP:INVALID_HALF_YEAR"
        http_status: 500 Internal Server Error
        message_template: "Invalid half-year number: {half}. Must be 1 or 2."
        is_retryable: False (requires valid half-year)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidHalfYear(half=3))
    """

    code = "APP:INVALID_HALF_YEAR"
    http_status = 500
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


class InvalidUsername(AppErrorDefinition):
    """Error definition for username validation failures in application logic.

    This error occurs at the application level when a username fails validation
    rules. This indicates a state inconsistency or logical error in the
    application where an invalid username is being processed.

    Attributes:
        code: "APP:INVALID_USERNAME"
        http_status: 500 Internal Server Error
        message_template: "Validation failed. Please check the provided data."
        is_retryable: False (requires valid username)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidUsername(
        ...     field_errors={"username": ["Must be at least 3 characters"]}
        ... ))
    """

    code = "APP:INVALID_USERNAME"
    http_status = 500
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
        """Initializes an invalid username error definition.

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


class InvalidTrustLevel(AppErrorDefinition):
    """Error definition for invalid trust level values in application logic.

    This error occurs at the application level when a provided trust level
    value is not one of the allowed values. This indicates a logical error
    in the application where an invalid trust level is being processed.

    Attributes:
        code: "APP:INVALID_TRUST_LEVEL"
        http_status: 500 Internal Server Error
        message_template: "Invalid trust level: {new_level}. Must be one of {allowed_levels}."
        is_retryable: False (requires valid trust level value)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidTrustLevel(
        ...     new_level="super_admin",
        ...     allowed_levels=["admin", "user", "guest"]
        ... ))
    """

    code = "APP:INVALID_TRUST_LEVEL"
    http_status = 500
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


class MissingClassAttribute(AppErrorDefinition):
    """Error definition for missing required class attributes.

    This error occurs at the application level when a class definition is
    missing required class attributes. This indicates a programming error
    in the class definition.

    Attributes:
        code: "APP:MISSING_CLASS_ATTRIBUTES"
        http_status: 500 Internal Server Error
        message_template: "Class '{class_name}' must define class attributes: {missing_attrs}."
        is_retryable: False (requires code correction)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(MissingClassAttribute(
        ...     class_name="MyErrorDefinition",
        ...     missing_attrs=["code", "http_status"]
        ... ))
    """

    code = "APP:MISSING_CLASS_ATTRIBUTES"
    http_status = 500
    message_template = _n(
        "Class '{class_name}' must define class attributes: {missing_attrs}."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        class_name: str | None = None,
        missing_attrs: list[str] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a missing class attributes error definition.

        Passes all arguments to the parent class constructor.
        """
        # Convert list to comma-separated string for the message template
        if "missing_attrs" in kwds and isinstance(kwds["missing_attrs"], list):
            kwds["missing_attrs"] = ", ".join(kwds["missing_attrs"])
        super().__init__(message_template, **kwds)


class InvalidAttributeType(AppErrorDefinition):
    """Error definition for invalid attribute type in class definitions.

    This error occurs at the application level when a class attribute is
    defined with an incorrect type. This indicates a programming error in
    the class definition.

    Attributes:
        code: "APP:INVALID_ATTRIBUTE_TYPE"
        http_status: 500 Internal Server Error
        message_template: "{class_name}.{attr_name} must be of type {expected_type}, got {actual_type}."
        is_retryable: False (requires code correction)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidAttributeType(
        ...     class_name="MyErrorDefinition",
        ...     attr_name="http_status",
        ...     expected_type="int",
        ...     actual_type="str"
        ... ))
    """

    code = "APP:INVALID_ATTRIBUTE_TYPE"
    http_status = 500
    message_template = _n(
        "{class_name}.{attr_name} must be of type {expected_type}, got {actual_type}."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        class_name: str | None = None,
        attr_name: str | None = None,
        expected_type: str | None = None,
        actual_type: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid attribute type error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class EmailNotNormalized(AppErrorDefinition):
    """Error definition for email addresses that are not properly normalized.

    This error occurs at the application level when an email address is
    provided in a non-normalized format. This indicates a logical error in
    the application where email normalization expectations are not met.

    Attributes:
        code: "APP:EMAIL_NOT_NORMALIZED"
        http_status: 500 Internal Server Error
        message_template: "Email '{provided}' is not normalized. Did you mean '{normalized}'?"
        is_retryable: False (requires using normalized email)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(EmailNotNormalized(
        ...     provided="User@Example.com",
        ...     normalized="user@example.com"
        ... ))
    """

    code = "APP:EMAIL_NOT_NORMALIZED"
    http_status = 500
    message_template = _n(
        "Email '{provided}' is not normalized. Did you mean '{normalized}'?"
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        provided: str | None = None,
        normalized: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an email not normalized error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidEmail(AppErrorDefinition):
    """Error definition for invalid email addresses in application logic.

    This error occurs at the application level when an email address doesn't
    meet the required format. This indicates a logical error in the application
    where an invalid email is being processed.

    Attributes:
        code: "APP:INVALID_EMAIL"
        http_status: 500 Internal Server Error
        message_template: "Email '{email}' is not valid."
        is_retryable: False (requires valid email address)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidEmail(email="invalid-email"))
    """

    code = "APP:INVALID_EMAIL"
    http_status = 500
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


class InvalidPhone(AppErrorDefinition):
    """Error definition for invalid phone numbers in application logic.

    This error occurs at the application level when a phone number doesn't
    meet the required format. This indicates a logical error in the application
    where an invalid phone number is being processed.

    Attributes:
        code: "APP:INVALID_PHONE"
        http_status: 500 Internal Server Error
        message_template: "Phone number '{number}' is not valid."
        is_retryable: False (requires valid phone number)

    Example:
        >>> # Wrap this definition in a validation-specific exception
        ... raise AppError(InvalidPhone(number="123456"))
    """

    code = "APP:INVALID_PHONE"
    http_status = 500
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


class DuplicateObject(AppErrorDefinition):
    """Error definition for duplicate object creation attempts.

    This error occurs at the application level when attempting to add an object
    to a collection or relationship where it already exists. This indicates a
    state inconsistency or logical error in the application where duplicate
    objects are being processed.

    Attributes:
        code: "APP:DUPLICATE_OBJECT"
        http_status: 409 Conflict
        message_template: "{object} with this {att_name} already exists."
        is_retryable: False (duplicate won't resolve by retrying)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(DuplicateObject(
        ...     object="User",
        ...     att_name="email"
        ... ))
    """

    code = "APP:DUPLICATE_OBJECT"
    http_status = 409
    message_template = _n("{object} with this {att_name} already exists.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        object: str | None = None,
        att_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a duplicate object error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ObjectNotFound(AppErrorDefinition):
    """Error definition for object lookup failures in application logic.

    This error occurs at the application level when a requested object cannot
    be found in the system. For example, when trying to add a non-existent
    object to a list or relationship. This indicates a logical error or
    state inconsistency in the application.

    Attributes:
        code: "APP:OBJECT_NOT_FOUND"
        http_status: 404 Not Found
        message_template: "{object} not found."
        is_retryable: False (object doesn't exist)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(ObjectNotFound(object="User"))
    """

    code = "APP:OBJECT_NOT_FOUND"
    http_status = 404
    message_template = _n("{object} not found.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        object: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an object not found error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class InvalidValue(AppErrorDefinition):
    """Error definition for invalid values in application operations.

    This error occurs at the application level when a value doesn't meet the
    expected requirements. This indicates a logical error in the application
    where an invalid value is being processed.

    Attributes:
        code: "APP:INVALID_VALUE"
        http_status: 500 Internal Server Error
        message_template: "Invalid value: {value}."
        is_retryable: False (requires valid value correction)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(InvalidValue(value="invalid_data"))
    """

    code = "APP:INVALID_VALUE"
    http_status = 500
    message_template = _n("Invalid value: {value}.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        value: Any | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid value error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class AttributeNotFound(AppErrorDefinition):
    """Error definition for missing attributes on objects.

    This error occurs at the application level when attempting to access an
    attribute that does not exist on an object. This indicates a programming
    error where the code expects an attribute that the object doesn't have.

    Attributes:
        code: "APP:ATTRIBUTE_NOT_FOUND"
        http_status: 500 Internal Server Error
        message_template: "'{object_type}' object has no attribute '{attribute_name}'."
        is_retryable: False (requires code correction)

    Example:
        >>> # Wrap this definition in an application-specific exception
        ... raise AppError(AttributeNotFound(
        ...     object_type="User",
        ...     attribute_name="non_existent_field"
        ... ))
    """

    code = "APP:ATTRIBUTE_NOT_FOUND"
    http_status = 500
    message_template = _n("'{object_type}' object has no attribute '{attribute_name}'.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        object_type: str,
        attribute_name: str,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an attribute not found error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
