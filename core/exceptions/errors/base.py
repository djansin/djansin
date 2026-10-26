"""Base error-definition primitives for standardized error representation.

This module defines :class:`ErrorDefinition` and its metaclass
:class:`ErrorMeta`, which together establish the framework for declaring
error blueprints across the application. An error definition is a
reusable, immutable-by-convention blueprint that specifies *how* an error
is represented: its error code, HTTP status, message template, and
retryability. Definitions are instantiated with context values to produce
dynamic, translated messages.

Important:
    This module is the foundation for *what an error looks like*
    (the blueprint). It does not raise anything. Runtime raising is
    handled by the exception layer, which wraps a definition.

    - Error definition class: "what the error looks like" (blueprint).
    - Exception class: "when the error happens" (raised in code flow).

Typical usage:
    Declare a subclass with the four required class attributes and
    instantiate it with context values::

        class InsufficientFunds(ErrorDefinition):
            code = "BIZ:INSUFFICIENT_FUNDS"
            http_status = 422
            message_template = (
                "Insufficient funds. Required: {required}, Available: {available}."
            )
            is_retryable = False

        error = InsufficientFunds(required=100.0, available=50.0)
        error.message  # formatted in the active language
"""

from abc import ABCMeta
from typing import Any, ClassVar

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _t, override


class ErrorMeta(ABCMeta):
    """Metaclass that validates and identifies ``ErrorDefinition`` subclasses.

    ``ErrorMeta`` enforces that every subclass of :class:`ErrorDefinition`
    declares the four required class attributes — ``code``, ``http_status``,
    ``message_template``, and ``is_retryable`` — with the exact expected
    types, and that ``http_status`` falls within the valid HTTP range
    (100–599). Validation is intentionally skipped for the
    ``ErrorDefinition`` base class itself, so the base may remain abstract.

    The metaclass also gives classes value-like semantics: they compare
    against string codes, hash by their code, and stringify to their code.

    Attributes:
        _required_attrs (dict[str, type]): Mapping of required attribute
            names to their expected Python types.
    """

    _required_attrs = {
        "code": str,
        "http_status": int,
        "message_template": str,
        "is_retryable": bool,
    }

    def __new__(mcs, name, bases, namespace, **kwds):
        """Create and validate a new ``ErrorDefinition`` subclass.

        Validates that all required class attributes exist with the correct
        types and that ``http_status`` is within the valid HTTP range.
        Validation is skipped for the ``ErrorDefinition`` base class.

        Args:
            name (str): Name of the class being created.
            bases (tuple[type, ...]): Base classes of the class being created.
            namespace (dict[str, Any]): Namespace of the class being created.
            **kwds (Any): Additional keyword arguments passed to
                ``ABCMeta.__new__``.

        Returns:
            type: The newly created and validated class.

        Raises:
            TypeError: If a required attribute is missing or has the wrong
                type.
            ValueError: If ``http_status`` is outside the range 100–599.
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
        """Compare the error class with a string code or another error class.

        Args:
            other (Any): The value to compare against. Either a string
                representing an error code or another ``ErrorDefinition``
                subclass.

        Returns:
            bool | NotImplemented: ``True`` if the codes match, ``False``
            otherwise, or ``NotImplemented`` for unsupported operand types.
        """
        if isinstance(other, str):
            return cls.code == other
        elif isinstance(other, cls):
            return other.__class__.code is cls.code
        return NotImplemented

    def __str__(cls) -> str:
        """Return the error code as the string representation.

        Returns:
            str: The error code.
        """
        return cls.code

    def __repr__(cls) -> str:
        """Return a detailed, debug-friendly representation of the class.

        Returns:
            str: A string of the form
            ``<ClassName: code='...', http_status=..., is_retryable=...>``.
        """
        return f"<{cls.__name__}: code='{cls.code}', http_status={cls.http_status}, is_retryable={cls.is_retryable}>"

    def __hash__(cls) -> int:
        """Return a hash derived from the error code.

        Returns:
            int: Hash of the class's error code.
        """
        return hash(cls.code)


class ErrorDefinition(metaclass=ErrorMeta):
    """Base class for all error definitions in the application.

    ``ErrorDefinition`` is the blueprint for every error in the system.
    Each subclass declares *how* a particular error is represented by
    overriding four required class attributes. Instances carry the
    resolved blueprint values plus optional context values used to format
    the message, and optional structured details.

    This class provides message formatting (translated and English),
    context management, selective instance derivation via :meth:`derive`,
    and dictionary serialization via :meth:`to_dict`.

    Subclasses must declare the following class attributes:
        code (str): Unique error code identifier
            (e.g. ``"BIZ_INSUFFICIENT_FUNDS"``).
        http_status (int): HTTP status code associated with the error,
            in the range 100–599.
        message_template (str): Message template containing ``{placeholder}``
            fields filled from instance context values.
        is_retryable (bool): Whether the failed operation may be retried.

    Attributes:
        _message_template (str): Instance-level message template.
        _code (str): Instance-level error code.
        _http_status (int): Instance-level HTTP status code.
        _is_retryable (bool): Instance-level retryability flag.
        _detail (dict[str, Any] | None): Structured error details, if any.
        _params (dict[str, Any]): Context values used to format the message.

    Example:
        >>> class InsufficientFunds(ErrorDefinition):
        ...     code = "BIZ_INSUFFICIENT_FUNDS"
        ...     http_status = 422
        ...     message_template = (
        ...         "Insufficient funds. Required: {required}, Available: {available}."
        ...     )
        ...     is_retryable = False
        >>>
        >>> error = InsufficientFunds(required=100.0, available=50.0)
        >>> error.message
        'Insufficient funds. Required: 100.0, Available: 50.0.'
    """

    code: ClassVar[str]
    http_status: ClassVar[int]
    message_template: ClassVar[str]
    is_retryable: ClassVar[bool]

    def __init__(
        self: "ErrorDefinition",
        message_template: str | None = None,
        /,
        *,
        _code: str | None = None,
        _http_status: int | None = None,
        _is_retryable: bool | None = None,
        _detail: dict[str, Any] | None = None,
        **params: Any,
    ) -> None:
        """Initialize an error definition instance.

        Instance values default to the class-level blueprint values. Any
        provided override replaces only the corresponding attribute. All
        remaining keyword arguments are captured as message-formatting
        context values.

        Args:
            message_template (str | None): Positional-only override for the
                message template. Defaults to the class template.
            _code (str | None): Override for the error code.
            _http_status (int | None): Override for the HTTP status code.
            _is_retryable (bool | None): Override for the retryability flag.
                Unlike other overrides, ``False`` is a valid value and is
                preserved.
            _detail (dict[str, Any] | None): Structured error details.
            **params (Any): Context values used to format the message
                template.
        """
        self._message_template = message_template or self.__class__.message_template
        self._code = _code or self.__class__.code
        self._http_status = _http_status or self.__class__.http_status
        self._is_retryable = (
            self.__class__.is_retryable if _is_retryable is None else _is_retryable
        )
        self._detail = _detail
        self._params = params

    @property
    def message_template(self) -> str:
        """Return the instance message template.

        Returns:
            str: The message template in use for this instance.
        """
        return self._message_template

    @property
    def code(self) -> str:
        """Return the instance error code.

        Returns:
            str: The error code in use for this instance.
        """
        return self._code

    @property
    def http_status(self) -> int:
        """Return the instance HTTP status code.

        Returns:
            int: The HTTP status code in use for this instance.
        """
        return self._http_status

    @property
    def is_retryable(self) -> bool:
        """Return whether the failed operation may be retried.

        Returns:
            bool: The retryability flag for this instance.
        """
        return self._is_retryable

    @property
    def message(self) -> str:
        """Return the formatted message in the active language.

        Formats the message template with the instance context values using
        the currently active language. Intended for display to end users in
        their preferred language.

        Returns:
            str: The formatted message in the active language.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            >>> error.message  # formatted in the active language
        """
        return format_lazy(_t(self.message_template), **self.params)

    @property
    def message_en(self) -> str:
        """Return the formatted message in English.

        Formats the message template with the instance context values using
        the English locale, regardless of the active language. Intended for
        logging and debugging where a stable language is desirable.

        Returns:
            str: The formatted message in English.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            >>> error.message_en
            'Insufficient funds. Required: 100.0, Available: 50.0.'
        """
        with override("en"):
            return format_lazy(_t(self.message_template), **self.params)

    @property
    def params(self) -> dict:
        """Return the context values used for message formatting.

        Returns:
            dict: The context dictionary. Empty if no values were supplied.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            >>> error.params
            {'required': 100.0, 'available': 50.0}
        """
        return self._params or {}

    @property
    def detail(self) -> dict:
        """Return the structured details for this error.

        If no details were provided at construction time, they are lazily
        initialized from :meth:`get_detail` and cached on the instance.

        Returns:
            dict: The structured details dictionary. May be empty.

        Example:
            >>> error = ValidationError(field_errors={"email": ["Invalid format"]})
            >>> error.detail
            {'field_errors': {'email': ['Invalid format']}}
        """
        if self._detail is None:
            self._detail = self.get_detail()
        return self._detail

    def get_detail(self) -> dict:
        """Provide structured details for the error.

        Hook intended for subclasses that need to compute structured
        details from instance state. The base implementation returns an
        empty dictionary.

        Returns:
            dict: A dictionary of structured error details.

        Example:
            >>> class ValidationError(ErrorDefinition):
            ...     def get_detail(self) -> dict:
            ...         return {
            ...             "field_errors": self._field_errors,
            ...             "non_field_errors": self._non_field_errors,
            ...         }
        """
        return {}

    def derive(
        self,
        /,
        *,
        message_template: str | None = None,
        code: str | None = None,
        http_status: int | None = None,
        is_retryable: bool | None = None,
        detail: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> "ErrorDefinition":
        """Create a new instance derived from this one.

        Builds a new instance of the same class using the current
        instance's values as defaults, applying only the provided overrides.
        When ``params`` is ``None``, the current context values are
        inherited; otherwise they are fully replaced by ``params``.

        Args:
            message_template (str | None): Override for the message template.
            code (str | None): Override for the error code.
            http_status (int | None): Override for the HTTP status code.
            is_retryable (bool | None): Override for the retryability flag.
                ``None`` preserves the current value.
            detail (dict[str, Any] | None): Override for the structured
                details.
            params (dict[str, Any] | None): Replacement context values. If
                ``None``, the current context is inherited.

        Returns:
            ErrorDefinition: A new instance with the requested overrides.

        Example:
            >>> base = InsufficientFunds(required=100.0, available=50.0)
            >>> custom = base.derive(code="CUSTOM_CODE")
        """
        new_instance = self.__class__(
            message_template or self.message_template,
            _code=code or self.code,
            _http_status=http_status or self.http_status,
            _is_retryable=self.is_retryable if is_retryable is None else is_retryable,
            _detail=detail or self.detail,
            **(self.params if params is None else params),
        )

        return new_instance

    def to_dict(self) -> dict:
        """Serialize the error definition to a dictionary.

        Produces a dictionary suitable for JSON responses or structured
        logging, containing the code, HTTP status, formatted message,
        retryability flag, and structured details.

        Returns:
            dict: A dictionary with keys ``code``, ``http_status``,
            ``message``, ``is_retryable``, and ``detail``.

        Example:
            >>> error = InsufficientFunds(required=100.0, available=50.0)
            >>> error.to_dict()
            {
                "code": "BIZ_INSUFFICIENT_FUNDS",
                "http_status": 422,
                "message": "Insufficient funds. Required: 100.0, Available: 50.0.",
                "is_retryable": False,
                "detail": {}
            }
        """
        return {
            "code": self.code,
            "http_status": self.http_status,
            "message": self.message,
            "is_retryable": self.is_retryable,
            "detail": self.detail,
        }

    def __eq__(self, other: Any) -> bool:
        """Compare this instance with a string code or another error.

        Args:
            other (Any): The value to compare against. Either a string
                error code or another :class:`ErrorDefinition` instance.

        Returns:
            bool | NotImplemented: ``True`` if the codes match, ``False``
            otherwise, or ``NotImplemented`` for unsupported operand types.
        """
        if isinstance(other, str):
            return self.code == other
        elif isinstance(other, ErrorDefinition):
            return self.code == other.code
        return NotImplemented

    def __str__(self) -> str:
        """Return the formatted message as the string representation.

        Returns:
            str: The formatted message in the active language.
        """
        return self.message

    def __repr__(self) -> str:
        """Return a detailed, debug-friendly representation of the instance.

        Returns:
            str: A string of the form
            ``ClassName(message_template='...', key1=value1, key2=value2)``.
        """
        params = ", ".join(f"{key}={value!r}" for key, value in self.params.items())
        return (
            f"{type(self).__name__}("
            f"message_template={self.message_template!r}"
            f"{', ' + params if params else ''}"
            f")"
        )

    def __hash__(self) -> int:
        """Return a hash derived from the error code.

        Returns:
            int: Hash of the instance error code.
        """
        return hash(self.code)
