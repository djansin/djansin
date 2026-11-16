"""Base exception primitives for the application's error-handling system.

This module defines the foundational runtime pieces that connect error
definitions (blueprints) to raised exceptions. It provides
:class:`ExceptionSeverity` for classifying how critical an error is, and
:class:`BaseAppException` — the base class every concrete application
exception inherits from.

Important:
    - :class:`ExceptionSeverity` classifies *how important* an error is,
      driving monitoring, alerting, and user-response policies.
    - :class:`BaseAppException` is the bridge that turns an
      :class:`~core.exceptions.errors.base.ErrorDefinition` into a raised
      Python exception, exposing a uniform interface for code, message,
      HTTP status, retryability, and structured details.

Key distinction:
    - Error definition classes: "what the error looks like" (blueprint).
    - Exception classes: "when the error happens" (raised in code flow).
    - Severity levels: "how important the error is" (monitoring priority).

Severity overrides at raise time:
    :class:`BaseAppException` exposes fluent helpers — ``with_severity``
    and one shortcut per severity level — that set the instance severity
    and return ``self``, so severity can be chosen directly in the
    ``raise`` expression::

        raise BusinessError(
            UserLocked(user_id=42),
        ).warning_severity()
"""

from enum import Enum, auto
from typing import Any, ClassVar, Generic, Self, TypeVar

from core.exceptions.errors.base import ErrorDefinition


class ExceptionSeverity(Enum):
    """Severity levels used to classify exceptions.

    Each member represents an increasing level of criticality, from
    development-only diagnostics (``DEBUG``) to catastrophic failures
    requiring service termination (``FATAL``). The convenience properties
    derive response policies — such as whether the error should surface in
    an admin panel or prompt the user to contact an administrator — directly
    from the severity level.

    Attributes:
        DEBUG (ExceptionSeverity): Development/debugging information; not
            typically surfaced to users.
        INFO (ExceptionSeverity): Informational events about normal
            operation.
        WARNING (ExceptionSeverity): Non-critical issues that may warrant
            attention.
        ERROR (ExceptionSeverity): Errors affecting functionality but not
            system stability.
        CRITICAL (ExceptionSeverity): Severe errors requiring immediate
            attention.
        FATAL (ExceptionSeverity): Catastrophic errors requiring service
            termination.
    """

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    FATAL = auto()

    @property
    def requires_admin_panel(self) -> bool:
        """Return whether the error should be surfaced in the admin panel.

        Returns:
            bool: ``True`` for ``ERROR``, ``CRITICAL``, and ``FATAL``;
            ``False`` otherwise.
        """
        return self in {self.ERROR, self.CRITICAL, self.FATAL}

    @property
    def requires_contact_admin(self) -> bool:
        """Return whether the user should be prompted to contact an admin.

        Returns:
            bool: ``True`` for ``CRITICAL`` and ``FATAL``; ``False``
            otherwise.
        """
        return self in {self.CRITICAL, self.FATAL}

    @property
    def requires_service_stop(self) -> bool:
        """Return whether the service should be stopped.

        Returns:
            bool: ``True`` only for ``FATAL``; ``False`` otherwise.
        """
        return self is self.FATAL


ErrorDefinitionType = TypeVar("ErrorDefinitionType", bound="ErrorDefinition")


class BaseAppException(Exception, Generic[ErrorDefinitionType]):
    """Base exception that wraps an :class:`ErrorDefinition` instance.

    This class is the foundation for every concrete application exception.
    It accepts either an existing error definition, a message-template
    string, or ``None``; in the latter two cases it constructs a definition
    from the class's :attr:`error_cls`. Overrides supplied via keyword
    arguments are applied through :meth:`ErrorDefinition.derive`, so the
    wrapped definition is always a fresh instance owned by the exception.

    Severity can be chosen at three points:

    1. As the class-level default via :attr:`severity`.
    2. As a per-instance override via the ``severity`` keyword argument.
    3. As a fluent override at raise time via :meth:`with_severity` or one
       of the ``*_severity`` shortcut methods, which set the instance
       severity and return ``self``.

    Subclasses must declare the following class attributes:
        error_cls (type[ErrorDefinitionType]): The error-definition class
            used when constructing a definition from a string or ``None``.
        severity (ExceptionSeverity): The default severity level applied
            when no per-instance severity is supplied.

    Attributes:
        _error (ErrorDefinitionType): The wrapped error definition.
        _severity (ExceptionSeverity): The severity for this instance,
            defaulting to the class-level :attr:`severity`.

    Example:
        >>> class BusinessError(BaseAppException):
        ...     error_cls = BizErrorDefinition
        ...     severity = ExceptionSeverity.ERROR
        >>>
        >>> raise BusinessError(
        ...     InsufficientFunds(required=100.0, available=50.0)
        ... )
        >>>
        >>> # Fluent severity override at raise time:
        ... raise BusinessError(
        ...     InsufficientFunds(required=100.0, available=50.0),
        ... ).critical_severity()
    """

    error_cls: ClassVar[type[ErrorDefinitionType]]
    severity: ClassVar[ExceptionSeverity]

    def __init__(
        self,
        error: str | ErrorDefinitionType | None = None,
        /,
        *,
        code: str | None = None,
        http_status: int | None = None,
        is_retryable: bool | None = None,
        detail: dict[str, Any] | None = None,
        severity: ExceptionSeverity | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception and its wrapped error definition.

        If ``error`` is a string or ``None``, a definition is built from
        :attr:`error_cls` using the given ``params`` as context. The
        resulting definition is then re-derived to apply any of the
        keyword overrides. The Python ``Exception`` message is set to
        :attr:`message`.

        Args:
            error (str | ErrorDefinitionType | None): An existing error
                definition, a message-template string, or ``None``.
                Positional-only.
            code (str | None): Override for the error code.
            http_status (int | None): Override for the HTTP status code.
            is_retryable (bool | None): Override for the retryability flag.
                ``None`` preserves the definition's current value.
            detail (dict[str, Any] | None): Structured error details.
            severity (ExceptionSeverity | None): Per-instance severity
                override. Defaults to the class-level :attr:`severity`.
            params (dict[str, Any] | None): Context values used to format
                the message template when building a definition from a
                string or ``None``.

        Example:
            >>> raise BusinessError(
            ...     InsufficientFunds(required=100.0, available=50.0)
            ... )
            >>> raise BusinessError("Custom message with {context}", key="value")
            >>> raise BusinessError(
            ...     InsufficientFunds(required=100.0, available=50.0),
            ...     code="CUSTOM_CODE",
            ...     http_status=400,
            ... )
        """
        if isinstance(error, str) or error is None:
            error_cls = self.__class__.error_cls
            error = error_cls(error, **(params or {}))

        self._error = error.derive(
            code=code,
            http_status=http_status,
            is_retryable=is_retryable,
            detail=detail,
        )
        self._severity = self.__class__.severity if severity is None else severity

        super().__init__(self.message)

    @property
    def error(self) -> ErrorDefinitionType:
        """Return the wrapped error definition.

        Returns:
            ErrorDefinitionType: The definition instance carried by this
            exception.
        """
        return self._error

    @property
    def message_en(self) -> str:
        """Return the formatted diagnostic message in English.

        Intended for logs, traces, and debugging. The message combines the
        severity name, the error code, and the English-formatted message.

        Returns:
            str: A string of the form
            ``[SEVERITY] CODE: message_en``.
        """
        return f"[{self.severity.name}] {self.error.code}: {self.error.message_en}"

    @property
    def message(self) -> str:
        """Return the formatted message in the active language.

        Intended for display to end users in their preferred language.

        Returns:
            str: The formatted message in the active language.
        """
        return self.error.message

    @message.setter
    def message(self, value: str) -> None:
        """Replace the underlying message template.

        Args:
            value (str): The new message template to use.
        """
        self._error = self.error.derive(message_template=value)

    @property
    def code(self) -> str:
        """Return the error code.

        Returns:
            str: The error code of the wrapped definition.
        """
        return self.error.get_code()

    @code.setter
    def code(self, value: str) -> None:
        """Override the error code.

        Args:
            value (str): The new error code.
        """
        self._error = self.error.derive(code=value)

    @property
    def detail(self) -> dict:
        """Return the structured details of the wrapped definition.

        Returns:
            dict: The structured details dictionary.
        """
        return self.error.detail

    @detail.setter
    def detail(self, value: dict) -> None:
        """Override the structured details.

        Args:
            value (dict): The new details dictionary.
        """
        self._error = self.error.derive(detail=value)

    @property
    def params(self) -> dict:
        """Return the context values used for message formatting.

        Returns:
            dict: The context dictionary of the wrapped definition.
        """
        return self.error.params

    @params.setter
    def params(self, value: dict) -> None:
        """Replace the context values used for message formatting.

        Args:
            value (dict): The new context dictionary.
        """
        self._error = self.error.derive(params=value)

    @property
    def http_status(self) -> int:
        """Return the HTTP status code.

        Returns:
            int: The HTTP status code of the wrapped definition.
        """
        return self.error.get_http_status()

    @http_status.setter
    def http_status(self, value: int) -> None:
        """Override the HTTP status code.

        Args:
            value (int): The new HTTP status code.
        """
        self._error = self.error.derive(http_status=value)

    @property
    def is_retryable(self) -> bool:
        """Return whether the failed operation may be retried.

        Returns:
            bool: ``True`` if the operation can be retried, ``False``
            otherwise.
        """
        return self.error.get_is_retryable()

    @is_retryable.setter
    def is_retryable(self, value: bool) -> None:
        """Override the retryability flag.

        Args:
            value (bool): The new retryability flag.
        """
        self._error = self.error.derive(is_retryable=value)

    @property
    def severity(self) -> ExceptionSeverity:
        """Return the severity of this exception instance.

        Returns:
            ExceptionSeverity: The per-instance severity if set, otherwise
            the class-level default.
        """
        return self._severity

    @severity.setter
    def severity(self, value: ExceptionSeverity) -> None:
        """Override the severity of this exception instance.

        Args:
            value (ExceptionSeverity): The new severity level.
        """
        self._severity = value

    def with_severity(self, severity: ExceptionSeverity) -> Self:
        """Set this instance's severity and return ``self`` for chaining.

        Enables fluent severity selection at raise time::

            raise UserLockedError(
                UserLockedDefinition(user_id=42),
            ).with_severity(ExceptionSeverity.WARNING)

        The method mutates the current instance rather than creating a new
        one, so the object returned is the same exception that will be
        raised.

        Args:
            severity (ExceptionSeverity): The severity level to apply.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.

        Example:
            >>> raise BusinessError(
            ...     InsufficientFunds(required=100.0, available=50.0),
            ... ).with_severity(ExceptionSeverity.CRITICAL)
        """
        self.severity = severity
        return self

    def debug_severity(self) -> Self:
        """Set severity to ``DEBUG`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.DEBUG)

    def info_severity(self) -> Self:
        """Set severity to ``INFO`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.INFO)

    def warning_severity(self) -> Self:
        """Set severity to ``WARNING`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`. Useful for
        raising an otherwise-``INFO`` error at ``WARNING`` level.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.WARNING)

    def error_severity(self) -> Self:
        """Set severity to ``ERROR`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.ERROR)

    def critical_severity(self) -> Self:
        """Set severity to ``CRITICAL`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.CRITICAL)

    def fatal_severity(self) -> Self:
        """Set severity to ``FATAL`` and return ``self``.

        Convenience wrapper around :meth:`with_severity`.

        Returns:
            BaseAppException[ErrorDefinitionType]: ``self``, for chaining.
        """
        return self.with_severity(ExceptionSeverity.FATAL)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the exception to a dictionary.

        Delegates to the wrapped definition so the output contains the
        code, HTTP status, formatted message, retryability flag, and
        structured details.

        Returns:
            dict[str, Any]: A JSON-friendly representation of the error.

        Example:
            >>> try:
            ...     raise BusinessError(
            ...         InsufficientFunds(required=100.0, available=50.0)
            ...     )
            ... except BusinessError as e:
            ...     payload = e.to_dict()
        """
        return self.error.to_dict()

    def __repr__(self) -> str:
        """Return a debug-friendly representation of the exception.

        Returns:
            str: A string of the form
            ``ClassName(error=<ErrorDefinition repr>)``.
        """
        return f"{type(self).__name__}(error={repr(self.error)})"
