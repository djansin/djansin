"""Base validator infrastructure for layered validation.

This module provides the abstract base class :class:`BaseValidator`, which
defines a reusable, framework-aware validation pipeline. Concrete
validators subclass it and implement only the ``validate`` method, while
inheriting normalization, blank-handling, error-factory selection, and
value-object semantics (equality, hashing, representation).

The design separates *what* is validated from *where* the validation
result is consumed. The same validator instance can be re-targeted for
different layers via :meth:`BaseValidator.for_input` and
:meth:`BaseValidator.for_domain`, producing shallow clones that raise the
appropriate error type (DRF input errors, domain errors, or the default
Django input errors).

Typical usage:
    >>> class AgeValidator(BaseValidator):
    ...     def validate(self, value):
    ...         if value < 0:
    ...             self.raise_validation_error("age.negative")
    >>> validator = AgeValidator(allow_blank=False, trim=True)
    >>> validator.run(" 42 ")
    '42'

Note:
    Instances are treated as immutable value objects. Use
    :meth:`for_input` or :meth:`for_domain` to obtain a re-targeted copy
    instead of mutating ``_error_factory`` directly.
"""

import copy
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar, Self, overload

from django.utils.deconstruct import deconstructible

from core.exceptions import DomainError, ValidationError
from core.exceptions.errors import ValidErrorDefinition
from core.exceptions.frameworks import DjangoInputError, DrfInputError


def _default_error_factory(error, **context):
    """Build the default validation error.

    Used as the fallback error factory for :class:`BaseValidator` when no
    explicit ``error_factory`` is provided.

    Args:
        error: The error identifier or definition describing the failure.
        **context: Additional context forwarded to the error constructor
            (for example, the offending value or field name).

    Returns:
        DjangoInputError: A Django-flavored input error instance.
    """
    return DjangoInputError(error, **context)


@deconstructible
class BaseValidator(ABC):
    """Abstract base class for all validators.

    Subclasses must implement :meth:`validate`. All other behavior —
    normalization, blank short-circuiting, error raising, and identity
    semantics — is provided by this base class.

    Attributes:
        default_error_factory (ClassVar[Callable[..., ValidationError]]):
            Factory used to build validation errors when no explicit
            ``error_factory`` is supplied. Defaults to
            :func:`_default_error_factory`, which produces
            :class:`DjangoInputError` instances.

    Args:
        allow_blank (bool): If ``True``, blank values bypass
            :meth:`validate` and are returned as-is. Defaults to ``True``.
        trim (bool): If ``True``, leading and trailing whitespace is
            stripped from string values during normalization. Defaults to
            ``False``.
        error_factory (Callable[..., ValidationError] | None): Callable
            that builds the exception raised on validation failure.
            Defaults to :attr:`default_error_factory`.
        **kwds: Additional keyword arguments preserved as part of the
            validator's identity for equality and hashing.

    Example:
        >>> class PositiveIntValidator(BaseValidator):
        ...     def validate(self, value):
        ...         if not isinstance(value, int) or value <= 0:
        ...             self.raise_validation_error("value.not_positive")
        >>> PositiveIntValidator(allow_blank=False).run(5)
        5
    """

    default_error_factory: ClassVar[Callable[..., ValidationError]] = staticmethod(
        _default_error_factory
    )

    @overload
    def __init__(
        self,
        /,
        *,
        allow_blank: bool = True,
        trim: bool = False,
        error_factory: Callable[..., ValidationError] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(
        self,
        /,
        **kwds,
    ) -> None:
        """Initialize the validator.

        Only the keyword arguments documented on the class are consumed;
        any additional keyword arguments are retained verbatim so that
        subclasses can participate in identity comparison without
        re-declaring a constructor.

        Args:
            **kwds: Configuration options. Recognized keys are
                ``allow_blank``, ``trim``, and ``error_factory``; all keys
                are preserved for identity purposes.
        """
        self._allow_blank = kwds.get("allow_blank", True)
        self._trim = kwds.get("trim", False)
        self._error_factory = kwds.get("error_factory", self.default_error_factory)

        self._kwds = kwds

    @property
    def allow_blank(self) -> bool:
        """bool: Whether blank values bypass validation."""
        return self._allow_blank

    @property
    def trim(self) -> bool:
        """bool: Whether string values are stripped during normalization."""
        return self._trim

    def for_input(self) -> Self:
        """Return a clone that raises DRF input errors.

        The clone shares all configuration with the current instance but
        uses :class:`DrfInputError` as its error factory. Intended for
        validators invoked at the API input boundary.

        Returns:
            Self: A shallow copy configured with the DRF input error
            factory.
        """
        return self._clone_with(self._input_error_factory)

    def for_domain(self) -> Self:
        """Return a clone that raises domain errors.

        The clone shares all configuration with the current instance but
        uses :class:`DomainError` as its error factory. Intended for
        validators invoked inside domain logic.

        Returns:
            Self: A shallow copy configured with the domain error factory.
        """
        return self._clone_with(self._domain_error_factory)

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Validate a normalized, non-blank value.

        Implementations should call :meth:`raise_validation_error` on
        failure and return ``None`` on success.

        Args:
            value (Any): The value to validate. It has already passed
                through :meth:`normalize` and has been confirmed as
                non-blank (or ``allow_blank`` is ``False``).

        Raises:
            ValidationError: If the value is invalid. Concrete
                implementations typically raise via
                :meth:`raise_validation_error` rather than raising
                directly.
        """

    def run(self, value: Any) -> Any:
        """Normalize, short-circuit blanks, and validate a value.

        This is the primary entry point for validation. The value is first
        passed through :meth:`normalize`. If ``allow_blank`` is ``True``
        and the normalized value is blank, it is returned without further
        checks. Otherwise :meth:`validate` is invoked.

        Args:
            value (Any): The value to normalize and validate.

        Returns:
            Any: The normalized value, whether or not validation ran.

        Raises:
            ValidationError: If :meth:`validate` rejects the value.
        """
        value = self.normalize(value)

        if self.allow_blank and self.is_blank(value):
            return value

        self.validate(value)
        return value

    def normalize(self, value: Any) -> Any:
        """Apply preprocessing to a value before validation.

        The default implementation strips whitespace from strings when
        :attr:`trim` is enabled. Subclasses may override to add further
        normalization.

        Args:
            value (Any): The raw value.

        Returns:
            Any: The normalized value.
        """
        if self._trim and isinstance(value, str):
            return value.strip()
        return value

    def is_blank(self, value: Any) -> bool:
        """Determine whether a value should be treated as blank.

        Blank values are ``None``, the empty string, or empty containers
        (``list``, ``tuple``, ``dict``, ``set``).

        Args:
            value (Any): The value to inspect.

        Returns:
            bool: ``True`` if the value is considered blank.
        """
        if value is None:
            return True
        if isinstance(value, str) and value == "":
            return True
        return isinstance(value, (list, tuple, dict, set)) and len(value) == 0

    def raise_validation_error(
        self, error: str | ValidErrorDefinition, **context: Any
    ) -> None:
        """Raise a validation error using the active error factory.

        Args:
            error (str | ValidErrorDefinition): The error identifier or
                definition describing the failure.
            **context (Any): Additional context forwarded to the error
                factory (for example, the offending value or field name).

        Raises:
            ValidationError: Always raised, built by the current error
                factory.
        """
        raise self._error_factory(error, **context)

    def __call__(self, value: Any) -> None:
        """Validate ``value`` in place, discarding the normalized result.

        Enables validators to be used as Django-style callables.

        Args:
            value (Any): The value to validate.

        Raises:
            ValidationError: If validation fails.
        """
        self.run(value)

    def __eq__(self, other: object) -> bool:
        """Compare validators by type and identity keyword arguments.

        The active error factory is intentionally excluded from the
        comparison so that ``for_input()`` and ``for_domain()`` clones
        remain equal to their source.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: ``True`` if both validators share the same concrete type
            and identity keyword arguments. Returns ``NotImplemented`` for
            unrelated types.
        """
        if type(other) is not type(self):
            return NotImplemented
        return self._identity_kwargs() == other._identity_kwargs()

    def __hash__(self) -> int:
        """Return a hash derived from the validator type and its kwargs.

        Returns:
            int: A hash consistent with :meth:`__eq__`.
        """
        kwargs = self._identity_kwargs()
        return hash(
            (type(self).__name__, tuple(sorted(kwargs.items(), key=lambda x: x[0])))
        )

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the validator.

        Returns:
            str: A representation including all identity keyword
            arguments.
        """
        kwargs = ", ".join(f"{k}={v!r}" for k, v in self._identity_kwargs().items())
        return f"{self.__class__.__name__}({kwargs})"

    def _identity_kwargs(self) -> dict[str, Any]:
        """Return the keyword arguments that define this validator's identity.

        Used by :meth:`__eq__`, :meth:`__hash__`, and :meth:`__repr__`.
        Subclasses may override to narrow or reshape the identity surface
        without changing the constructor.

        Returns:
            dict[str, Any]: The raw keyword arguments captured at
            construction time.
        """
        return self._kwds

    def _clone_with(self, error_factory: Callable[..., ValidationError]) -> Self:
        """Return a shallow copy of this validator bound to another error factory.

        All configuration is preserved; only the active error factory is
        replaced. Because the clone is shallow, any mutable state shared
        with the original remains shared, which is acceptable since
        validators are treated as immutable value objects.

        Args:
            error_factory (Callable[..., ValidationError]): The factory to
                install on the clone.

        Returns:
            Self: A new validator instance using ``error_factory``.
        """
        clone = copy.copy(self)
        clone._error_factory = error_factory
        return clone

    @staticmethod
    def _input_error_factory(error, **context):
        """Build a DRF input error.

        Installed on clones produced by :meth:`for_input`, so that
        validation failures surface as API-layer input errors.

        Args:
            error: The error identifier or definition describing the failure.
            **context: Additional context forwarded to the error constructor.

        Returns:
            DrfInputError: A DRF-flavored input error instance.
        """
        return DrfInputError(error, **context)

    @staticmethod
    def _domain_error_factory(error, **context):
        """Build a domain error.

        Installed on clones produced by :meth:`for_domain`, so that
        validation failures surface as domain-layer errors rather than
        input errors.

        Args:
            error: The error identifier or definition describing the failure.
            **context: Additional context forwarded to the error constructor.

        Returns:
            DomainError: A domain error instance.
        """
        return DomainError(error, **context)
