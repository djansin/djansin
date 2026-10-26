"""Category-specific base exception classes for the error-handling system.

This module defines the foundational category base exception classes that
organize the application's error hierarchy. Each class binds a category of
error definitions (from :mod:`core.exceptions.errors.categories`) to a default
:class:`~core.exceptions.base.ExceptionSeverity`, establishing *when* and
*why* errors in that category occur and how they should be treated by
monitoring and alerting.

Important:
    Every class in this module is a **category base**. It may be used in
    either of two ways:

    1. **Raised directly**, with an explicit error definition as the
       diagnostic identifier. This is the categories case when the caller
       needs to signal only the category and the specific error identity
       is already carried by the definition passed to the constructor::

           raise ValidationError(InvalidLoginIdentifier())

       Callers can then catch the broad category with a single
       ``except ValidationError`` clause and discriminate the specific
       error through ``exc.error == InvalidLoginIdentifier`` or
       ``exc.error.code``.

    2. **Subclassed**, to bind a more specific ``error_cls`` for a
       recurring scenario and give the exception a named home in the
       codebase::

           class ModelFieldNotFoundError(AppError):
               error_cls = ModelFieldNotFound

           raise ModelFieldNotFoundError(
               field_name="foo", model_name="User"
           )

    In both cases the *category* is what makes the exception catchable
    by one ``except`` clause, while the *error definition* carried in
    ``exc.error`` is what identifies the specific error.

Key distinction:
    - Error-definition classes: "what the error looks like" (blueprint).
    - Category base exception classes (this module): "which category
      the error belongs to and how severe it is by default". They are
      both directly raisable and subclassable.
    - Concrete exception classes (defined elsewhere): "when a specific
      error happens", usually produced by subclassing one of these
      category bases and binding a concrete ``error_cls``.

Validation is split into two layers, each represented by its own
category base:
    - :class:`InputError`: structural/type validation in the data layer
      (serializers, forms, field validators). Raised before domain logic
      runs.
    - :class:`DomainError`: business-rule validation in the service layer.
      Raised when the input is structurally valid but domain invariants
      are violated.
"""

from core.exceptions.base import BaseAppException, ExceptionSeverity
from core.exceptions.errors.categories import (
    AppErrorDefinition,
    AuthErrorDefinition,
    BizErrorDefinition,
    DbErrorDefinition,
    ExtErrorDefinition,
    HttpErrorDefinition,
    SysErrorDefinition,
    ValidErrorDefinition,
)


class AppError(BaseAppException[AppErrorDefinition]):
    """Category base for generic, unclassified application errors.

    Catch-all category for errors that do not fit into a more specific
    one. May be raised directly with an explicit
    :class:`AppErrorDefinition` as the diagnostic identifier, or
    subclassed to bind a concrete ``error_cls`` for a recurring scenario.

    Severity:
        ERROR — unexpected application issues that require investigation
        but not an immediate service stop.

    Typical scenarios:
        - Unexpected internal state.
        - Unhandled edge cases.
        - Fallback when no more specific category applies.

    Attributes:
        error_cls (type[AppErrorDefinition]): Default error-definition
            class used when the constructor is called with a string or
            ``None``. Subclasses typically override it with a more
            specific definition.
        severity (ExceptionSeverity): Default severity, ``ERROR``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.app import ModelFieldNotFound
        ... raise AppError(
        ...     ModelFieldNotFound(field_name="foo", model_name="User")
        ... )
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class ModelFieldNotFoundError(AppError):
        ...     error_cls = ModelFieldNotFound
        ... raise ModelFieldNotFoundError(
        ...     field_name="foo", model_name="User"
        ... )
    """

    error_cls = AppErrorDefinition
    severity = ExceptionSeverity.ERROR


class AuthError(BaseAppException[AuthErrorDefinition]):
    """Category base for authentication and authorization errors.

    Covers failures in establishing or validating identity and in
    enforcing access-control decisions. May be raised directly with an
    explicit :class:`AuthErrorDefinition`, or subclassed to bind a
    concrete ``error_cls``.

    Severity:
        INFO — authentication failures are expected operational
        occurrences and do not, by themselves, indicate system problems.

    Typical scenarios:
        - Invalid login credentials.
        - Expired or malformed tokens.
        - Insufficient permissions for the requested action.
        - Locked or inactive accounts.

    Attributes:
        error_cls (type[AuthErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``INFO``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.auth import InvalidToken
        ... raise AuthError(InvalidToken())
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class InvalidTokenError(AuthError):
        ...     error_cls = InvalidToken
        ... raise InvalidTokenError()
    """

    error_cls = AuthErrorDefinition
    severity = ExceptionSeverity.INFO


class BusinessError(BaseAppException[BizErrorDefinition]):
    """Category base for business-logic violations.

    Represents rejections of an operation because of domain rules,
    resource state, or policy constraints — independent of input shape.
    May be raised directly with an explicit :class:`BizErrorDefinition`,
    or subclassed to bind a concrete ``error_cls``.

    Severity:
        INFO — business-rule violations are normal application behavior,
        though some may indicate misuse patterns worth reviewing.

    Typical scenarios:
        - Duplicate resource creation.
        - Operation not allowed in the current state.
        - Quota or rate-limit exceedance.
        - Resource not found.

    Attributes:
        error_cls (type[BizErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``INFO``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.biz import InsufficientFunds
        ... raise BusinessError(
        ...     InsufficientFunds(required=100.0, available=50.0)
        ... )
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class InsufficientFundsError(BusinessError):
        ...     error_cls = InsufficientFunds
        ... raise InsufficientFundsError(required=100.0, available=50.0)
    """

    error_cls = BizErrorDefinition
    severity = ExceptionSeverity.INFO


class DatabaseError(BaseAppException[DbErrorDefinition]):
    """Category base for database-operation errors.

    Covers failures originating from the persistence layer, whether
    caused by infrastructure problems or data-integrity conflicts. May
    be raised directly with an explicit :class:`DbErrorDefinition`, or
    subclassed to bind a concrete ``error_cls``.

    Severity:
        ERROR — typically indicates infrastructure problems or data
        consistency issues that require attention.

    Typical scenarios:
        - Database connection loss.
        - Unique or foreign-key constraint violations.
        - Deadlocks and serialization conflicts.
        - Query execution failures.

    Attributes:
        error_cls (type[DbErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``ERROR``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.db import DbConnection
        ... raise DatabaseError(DbConnection())
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class DbConnectionError(DatabaseError):
        ...     error_cls = DbConnection
        ... raise DbConnectionError()
    """

    error_cls = DbErrorDefinition
    severity = ExceptionSeverity.ERROR


class ExternalError(BaseAppException[ExtErrorDefinition]):
    """Category base for failures originating from external services.

    Covers errors raised by third-party integrations such as APIs,
    payment gateways, and email providers. May be raised directly with
    an explicit :class:`ExtErrorDefinition`, or subclassed to bind a
    concrete ``error_cls``.

    Severity:
        ERROR — external failures affect functionality and need
        monitoring, though they may be transient.

    Typical scenarios:
        - Third-party API unavailable or returning an error.
        - Payment processing failure.
        - Email delivery failure.
        - External service timeout or connectivity issue.

    Attributes:
        error_cls (type[ExtErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``ERROR``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.ext import ExtApi
        ... raise ExternalError(ExtApi(reference_id="API-12345"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class ExternalApiError(ExternalError):
        ...     error_cls = ExtApi
        ... raise ExternalApiError(reference_id="API-12345")
    """

    error_cls = ExtErrorDefinition
    severity = ExceptionSeverity.ERROR


class HttpError(BaseAppException[HttpErrorDefinition]):
    """Category base for HTTP-protocol-level errors.

    Represents failures expressed in terms of HTTP semantics rather
    than a specific domain rule. May be raised directly with an explicit
    :class:`HttpErrorDefinition`, or subclassed to bind a concrete
    ``error_cls``.

    Severity:
        INFO — normal client–server communication issues that do not
        indicate system problems.

    Typical scenarios:
        - Bad request (400) due to missing or malformed parameters.
        - Resource not found (404).
        - Authentication required (401) or forbidden (403).
        - Method not allowed (405).
        - Rate limit exceeded (429).

    Attributes:
        error_cls (type[HttpErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``INFO``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.http import NotFound
        ... raise HttpError(NotFound(resource="Product"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class NotFoundError(HttpError):
        ...     error_cls = NotFound
        ... raise NotFoundError(resource="Product")
    """

    error_cls = HttpErrorDefinition
    severity = ExceptionSeverity.INFO


class SystemError(BaseAppException[SysErrorDefinition]):
    """Category base for system-level errors.

    Represents failures of the runtime environment, service
    availability, or application configuration rather than of a
    specific domain rule. May be raised directly with an explicit
    :class:`SysErrorDefinition`, or subclassed to bind a concrete
    ``error_cls``.

    Severity:
        ERROR — indicates infrastructure or configuration problems
        that require attention. Concrete subclasses may escalate to
        ``CRITICAL`` when the condition is severe.

    Typical scenarios:
        - Unhandled internal exceptions.
        - Service overload or maintenance mode.
        - Request timeout.
        - Missing or invalid configuration.

    Attributes:
        error_cls (type[SysErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``ERROR``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.sys import ServiceUnavailable
        ... raise SystemError(ServiceUnavailable())
        >>>
        >>> # Subclassing to bind a concrete error_cls, escalating severity:
        ... class ServiceUnavailableError(SystemError):
        ...     error_cls = ServiceUnavailable
        ... raise ServiceUnavailableError().critical_severity()
    """

    error_cls = SysErrorDefinition
    severity = ExceptionSeverity.ERROR


class ValidationError(BaseAppException[ValidErrorDefinition]):
    """Category base for every validation-related exception.

    The shared ancestor that makes it possible to catch *every*
    validation failure with a single ``except ValidationError`` clause,
    regardless of whether the failure originated in the data layer
    (framework-specific input errors) or the service layer
    (:class:`DomainError`).

    May be raised directly with an explicit
    :class:`~core.exceptions.errors.categories.ValidErrorDefinition` as the
    diagnostic identifier, or subclassed to bind a more specific
    ``error_cls`` or to add framework-specific behavior.

    Severity:
        ERROR — a directly raised :class:`ValidationError` signals a
        validation guard that has already failed at a layer where the
        condition is not expected to reach user code, so it is treated
        as an application error. The concrete subclasses
        (:class:`InputError`, :class:`DomainError`) deliberately
        lower this to ``INFO`` because they represent expected,
        recoverable user-facing failures.

    Attributes:
        error_cls (type[ValidErrorDefinition]): Default error-definition
            class used when the constructor is called with a string or
            ``None``. Subclasses typically override it with a more
            specific definition.
        severity (ExceptionSeverity): Default severity, ``ERROR``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from apps.authentication.exceptions import InvalidLoginIdentifier
        ... raise ValidationError(InvalidLoginIdentifier())
        >>>
        >>> # Catching the entire validation category:
        ... try:
        ...     ...
        ... except ValidationError as exc:
        ...     assert exc.error == InvalidLoginIdentifier
    """

    error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.ERROR


class InputError(ValidationError):
    """Category base for framework-neutral input validation failures.

    Represents violations of the expected *shape* of the input data,
    independent of any business rule. Intended for validators that run
    outside DRF serializers and Django forms, or for code that needs a
    framework-neutral validation category.

    For validation that runs inside a DRF serializer or a Django form,
    prefer :class:`~core.exceptions.validation.DrfInputError` or
    :class:`~core.exceptions.validation.DjangoInputError`
    respectively, so that the raised exception is recognized by the
    framework's own validation machinery.

    May be raised directly with an explicit validation definition
    (typically from :mod:`core.exceptions.errors.validation`), or
    subclassed to bind a concrete ``error_cls``.

    Typical scenarios:
        - Missing required field.
        - Invalid format for email, phone, or national code.
        - Field length below the minimum or above the maximum.
        - Value outside the allowed range or not matching the required
          pattern.
        - Wrong primitive type (e.g. a string where an integer is
          expected).

    Attributes:
        error_cls (type[ValidErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``INFO``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.validation import InvalidEmail
        ... raise InputError(InvalidEmail(email="invalid@"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class InvalidEmailError(InputError):
        ...     error_cls = InvalidEmail
        ... raise InvalidEmailError(email="invalid@")
    """

    error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.INFO


class DomainError(ValidationError):
    """Category base for business-rule violations in the service layer.

    Represents failures of domain invariants and cross-field
    consistency rules that cannot be expressed by structural validation
    alone. The input is assumed to be structurally valid; only the
    meaning of the data within the current domain state is rejected. May
    be raised directly with an explicit validation definition, or
    subclassed to bind a concrete ``error_cls``.

    Typical scenarios:
        - Uniqueness violation of a natural key (e.g. duplicate national
          code).
        - State conflict (e.g. an address is default while being
          deleted).
        - Cross-aggregate rule (e.g. shipping to a blocked province).
        - Policy violation (e.g. a user must verify their phone number
          before ordering).

    Attributes:
        error_cls (type[ValidErrorDefinition]): Default error-definition
            class for this category. Subclasses typically override it.
        severity (ExceptionSeverity): Default severity, ``INFO``.

    Example:
        >>> # Direct raise with an explicit definition:
        ... from core.exceptions.errors.validation import RequiredField
        ... raise DomainError(RequiredField(field="phone"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class PhoneNotVerifiedError(DomainError):
        ...     error_cls = RequiredField
        ... raise PhoneNotVerifiedError(field="phone")
    """

    error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.INFO
