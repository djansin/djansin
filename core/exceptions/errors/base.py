"""Provides the base error definition class for standardized error representation.

This module defines the foundational ErrorDefinition class and its metaclass
ErrorMeta, which together establish a robust framework for declaring and
managing error definitions across the application. Error definitions serve
as blueprints that specify how errors should be represented, including their
error codes, HTTP status codes, message templates, and retryability.

IMPORTANT - What this class represents:
    - This is the BASE ERROR DEFINITION (blueprint) for ALL error types
    - Each subclass declares HOW an error should be represented
    - Defines the error code, HTTP status, message template, and retryability
    - Can be instantiated with custom context values for dynamic messages

Key distinction:
    - ErrorDefinition class = "WHAT the error looks like" (blueprint/definition)
    - Exception classes = "WHEN the error happens" (raised in code flow)
"""

from abc import ABCMeta
from typing import Any, ClassVar, overload

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _t, override


class ErrorMeta(ABCMeta):
    """Metaclass for ErrorDefinition that enforces required class attributes.

    This metaclass validates that all ErrorDefinition subclasses define the
    required class attributes: code, http_status, message_template, and
    is_retryable. It also validates the types of these attributes and ensures
    http_status falls within the valid HTTP status code range (100-599).

    Attributes:
        _required_attrs: Mapping of required attribute names to their expected types.

    Raises:
        TypeError: When required attributes are missing or have incorrect types.
        ValueError: When http_status is outside the valid range (100-599).
    """

    _required_attrs = {
        "code": str,
        "http_status": int,
        "message_template": str,
        "is_retryable": bool,
    }

    def __new__(mcs, name, bases, namespace, **kwds):
        """Creates a new ErrorDefinition subclass with validation.

        Validates that all required class attributes exist and have the correct
        types. Skips validation for the ErrorDefinition base class itself.

        Args:
            name: The name of the class being created.
            bases: The base classes of the class being created.
            namespace: The namespace dictionary of the class being created.
            **kwds: Additional keyword arguments.

        Returns:
            The created class instance.

        Raises:
            TypeError: If required attributes are missing or have incorrect types.
            ValueError: If http_status is outside the valid range.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwds)

        # Skip validation for base classes (ErrorDefinition itself)
        if name == "ErrorDefinition":
            return cls

        # Validate required attributes exist
        missing = [attr for attr in mcs._required_attrs if not hasattr(cls, attr)]

        if missing:
            raise TypeError(
                f"Class {name} must define class attributes: {', '.join(missing)}"
            )

        for attr, expected_type in mcs._required_attrs.items():
            actual_value = getattr(cls, attr)
            actual_type = type(actual_value)

            if expected_type is actual_type:
                continue

            raise TypeError(
                f"{name}.{attr} must be of type {expected_type.__name__}, "
                f"got {actual_type.__name__}"
            )

        if cls.http_status < 100 or cls.http_status > 599:
            raise ValueError(
                f"{name}.http_status must be between 100 and 599, got {cls.http_status}"
            )

        return cls

    def __eq__(cls, other: Any) -> bool:
        """Compares the error class with a string code or another error class.

        Args:
            other: The object to compare with (string code or ErrorDefinition subclass).

        Returns:
            True if the error codes match, False otherwise.
        """
        if isinstance(other, str):
            return cls.code == other
        elif isinstance(other, cls):
            return other.__class__.code is cls.code
        return NotImplemented

    def __str__(cls) -> str:
        """Returns the error code as the string representation.

        Returns:
            The error code string.
        """
        return cls.code

    def __repr__(cls) -> str:
        """Returns a detailed representation of the error class.

        Returns:
            A string containing the class name, code, http_status, and is_retryable.
        """
        return f"<{cls.__name__}: code='{cls.code}', http_status={cls.http_status}, is_retryable={cls.is_retryable}>"

    def __hash__(cls) -> int:
        """Returns a hash based on the error code.

        Returns:
            The hash of the error code string.
        """
        return hash(cls.code)


class ErrorDefinition(metaclass=ErrorMeta):
    """Base class for all error definitions in the application.

    ErrorDefinition serves as the foundation for declaring error blueprints
    that specify how different types of errors should be represented. It
    provides functionality for message formatting, context management,
    instance derivation, and dictionary serialization.

    Class Attributes:
        code: The unique error code identifier (e.g., "BIZ_INSUFFICIENT_FUNDS").
        http_status: The HTTP status code associated with the error.
        message_template: The message template with placeholders for context.
        is_retryable: Whether the operation can be retried.

    Attributes:
        message_template: Instance-specific message template.
        code: Instance-specific error code.
        http_status: Instance-specific HTTP status code.
        is_retryable: Instance-specific retryability flag.
        _context: Dictionary of context variables for message formatting.
        _details: Optional dictionary for structured error details.

    Example:
        >>> # Define a custom error definition
        ... class InsufficientFunds(ErrorDefinition):
        ...    code = "BIZ_INSUFFICIENT_FUNDS"
        ...    http_status = 422
        ...    message_template = "Insufficient funds. Required: {required}, Available: {available}."
        ...    is_retryable = False

        >>> # Instantiate with context values
        ... error = InsufficientFunds(required=100.0, available=50.0)
        ... print(error.message)  # "Insufficient funds. Required: 100.0, Available: 50.0."
    """

    code: ClassVar[str]
    http_status: ClassVar[int]
    message_template: ClassVar[str]
    is_retryable: ClassVar[bool]

    @classmethod
    def instance_with(
        cls,
        message_template: str | None = None,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _details: dict[str, Any] | None = None,
        **context,
    ) -> "ErrorDefinition":
        """Creates a new ErrorDefinition instance with optional overrides.

        This class method provides a factory-style way to create instances
        with custom attributes while maintaining the class's default values
        for unspecified parameters.

        Args:
            message_template: Optional custom message template override.
            _code: Optional custom error code override.
            _http_status: Optional custom HTTP status code override.
            _is_retryable: Optional custom retryability flag override.
            _details: Optional structured details dictionary.
            **context: Context values for message formatting.

        Returns:
            A new ErrorDefinition instance with the specified attributes.

        Example:
            >>> error = InsufficientFunds.instance_with(
            ...     required=100.0,
            ...     available=50.0,
            ...     _code="CUSTOM_CODE"
            ... )
        """
        instance = cls(
            message_template or cls.message_template,
            _code=_code,
            _http_status=_http_status,
            _is_retryable=_is_retryable,
            _details=_details,
            **context,
        )
        return instance

    @overload
    def __init__(self: "ErrorDefinition", /, **context) -> None: ...

    @overload
    def __init__(
        self: "ErrorDefinition",
        message_template: str,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _details: dict[str, Any] | None = None,
        **context,
    ) -> None: ...

    def __init__(
        self: "ErrorDefinition",
        message_template: str | None = None,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _details: dict[str, Any] | None = None,
        **context,
    ) -> None:
        """Initializes a new ErrorDefinition instance.

        Args:
            message_template: Optional custom message template override.
            _code: Optional custom error code override.
            _http_status: Optional custom HTTP status code override.
            _is_retryable: Optional custom retryability flag override.
            _details: Optional structured details dictionary.
            **context: Context values for message formatting.
        """
        self.message_template = message_template or self.__class__.message_template
        self.code = _code or self.__class__.code
        self.http_status = _http_status or self.__class__.http_status
        self.is_retryable = (
            self.__class__.is_retryable if _is_retryable is None else _is_retryable
        )
        self._details = _details
        self._context = context

    @property
    def message(self) -> str:
        """Returns the formatted error message in English.

        This property formats the message template with the provided context
        values using the English locale. Useful for logging and debugging
        where consistent English messages are desired.

        Returns:
            The formatted message string in English.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            ... print(error.message)  # "Insufficient funds. Required: 100.0, Available: 50.0."
        """
        with override("en"):
            return format_lazy(_t(self.message_template), **self.context)

    @property
    def user_message(self) -> str:
        """Returns the formatted error message in the active language.

        This property formats the message template with the provided context
        values using the current active language. Suitable for displaying
        error messages to end users in their preferred language.

        Returns:
            The formatted message string in the active language.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            ... print(error.user_message)  # Formatted in current language
        """
        return format_lazy(_t(self.message_template), **self.context)

    @property
    def context(self) -> dict:
        """Returns the context dictionary for message formatting.

        Returns:
            The dictionary of context values used for message formatting.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            ... print(error.context)  # {'required': 100.0, 'available': 50.0}
        """
        return self._context or {}

    @property
    def details(self) -> dict:
        """Returns the structured details for the error.

        This property lazily initializes details if they haven't been set yet
        by calling get_details().

        Returns:
            The structured details dictionary.

        Example:
            >>> error = ValidationError(field_errors={"email": ["Invalid format"]})
            ... print(error.details)  # {'field_errors': {'email': ['Invalid format']}}
        """
        if self._details is None:
            self._details = self.get_details()
        return self._details

    def get_details(self) -> dict:
        """Hook for subclasses to provide structured error details.

        This method should be overridden by subclasses that need to provide
        additional structured information about the error. By default,
        returns an empty dictionary.

        Returns:
            A dictionary containing structured error details.

        Example:
            >>> class ValidationError(ErrorDefinition):
            ...    def get_details(self) -> dict:
            ...        return {
            ...            "field_errors": self._field_errors,
            ...            "non_field_errors": self._non_field_errors,
            ...        }
        """
        return {}

    def derive(
        self,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _details: dict[str, Any] | None = None,
    ) -> "ErrorDefinition":
        """Creates a new instance by deriving from the current one.

        This method creates a new ErrorDefinition instance using the current
        instance's attributes as defaults, allowing selective overrides of
        specific attributes.

        Args:
            _code: Optional custom error code override.
            _http_status: Optional custom HTTP status code override.
            _is_retryable: Optional custom retryability flag override.
            _details: Optional structured details dictionary.

        Returns:
            A new ErrorDefinition instance with the specified overrides.

        Example:
            >>> base_error = InsufficientFunds(required=100.0, available=50.0)
            ... custom_error = base_error.derive(_code="CUSTOM_CODE")
        """
        new_instance = self.__class__(
            self.message_template,
            _code=_code or self.code,
            _http_status=_http_status or self.http_status,
            _is_retryable=self.is_retryable if _is_retryable is None else _is_retryable,
            _details=_details or self.details,
            **self.context,
        )

        return new_instance

    def to_dict(self) -> dict:
        """Converts the error definition to a dictionary representation.

        This method serializes the error definition into a dictionary
        suitable for JSON responses or logging.

        Returns:
            A dictionary containing the error code, HTTP status, user message,
            retryability flag, and structured details.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            ... print(error.to_dict())
            ... # {
            ... #     "code": "BIZ_INSUFFICIENT_FUNDS",
            ... #     "http_status": 422,
            ... #     "message": "Insufficient funds. Required: 100.0, Available: 50.0.",
            ... #     "is_retryable": False,
            ... #     "details": {}
            ... # }
        """
        return {
            "code": self.code,
            "http_status": self.http_status,
            "message": self.user_message,
            "is_retryable": self.is_retryable,
            "details": self.details,
        }

    def __eq__(self, other: Any) -> bool:
        """Compares the error instance with a string code or another error.

        Args:
            other: The object to compare with (string code or ErrorDefinition).

        Returns:
            True if the error codes match, False otherwise.
        """
        if isinstance(other, str):
            return self.code == other
        elif isinstance(other, ErrorDefinition):
            return self.code == other.code
        return NotImplemented

    def __str__(self) -> str:
        """Returns the formatted user message as the string representation.

        Returns:
            The formatted user message string.
        """
        return self.message

    def __repr__(self) -> str:
        """Returns a detailed representation of the error instance.

        Returns:
            A string containing the class name and context values.
        """
        return (
            f"{self.__class__.__name__}({self.context})"
            if self.context
            else f"{self.__class__.__name__}()"
        )

    def __hash__(self) -> int:
        """Returns a hash based on the error code.

        Returns:
            The hash of the error code string.
        """
        return hash(self.code)
