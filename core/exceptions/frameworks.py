"""Framework-specific input validation exception classes.

This module provides the concrete category bases that adapt the
framework-neutral validation hierarchy to Django and Django REST
Framework. Each class mixes in the corresponding framework's own
validation exception so that the raised error is recognized by the
framework's validation machinery — DRF exception handlers, Django form
cleaning, and field validators — while still belonging to the
application's validation category tree.

Important:
    These classes are the ones to raise from code that runs *inside* a
    framework boundary:

    - :class:`DrfInputError` — for DRF serializers and DRF field
      validators.
    - :class:`DjangoInputError` — for Django forms and Django model
      field validators.

    The framework-neutral :class:`~core.exceptions.categories.InputError`
    remains available for validation that runs outside either framework,
    but it is not recognized as a native validation error by DRF or
    Django. Using the wrong base from inside a framework boundary will
    cause the error to surface as an unhandled 500 instead of a
    structured validation response.

Key distinction:
    - Error-definition classes: "what the error looks like" (blueprint).
    - Category base exception classes: "which category the error
      belongs to and how severe it is by default". They are both
      directly raisable and subclassable.
    - Framework-specific input errors (this module): category bases that
      additionally mix in a framework's native validation exception.
    - Concrete exception classes (defined elsewhere): "when a specific
      error happens", usually produced by subclassing one of the
      category bases and binding a concrete ``error_cls``.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.exceptions.base import ExceptionSeverity
from core.exceptions.categories import ValidationError
from core.exceptions.errors.categories import ValidErrorDefinition


class DrfInputError(ValidationError, DRFValidationError):
    """Input validation failure raised inside a DRF boundary.

    Represents violations of the expected *shape* of the input data,
    independent of any business rule. Intended to be raised by DRF
    serializers and DRF field validators — that is, before domain logic
    runs.

    Mixes in :class:`rest_framework.exceptions.ValidationError` so that
    DRF's exception handler recognizes the instance as a native
    validation failure and produces a structured 400 response instead of
    treating it as an unhandled server error. At the same time, it
    remains part of the application's :class:`ValidationError` category
    tree, so ``except ValidationError`` catches it.

    May be raised directly with an explicit validation definition
    (typically from :mod:`core.exceptions.errors.validation`), or
    subclassed to bind a concrete ``error_cls`` for a recurring
    scenario.

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
        ... raise DrfInputError(InvalidEmail(email="invalid@"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class InvalidEmailError(DrfInputError):
        ...     error_cls = InvalidEmail
        ... raise InvalidEmailError(email="invalid@")
    """

    error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.INFO


class DjangoInputError(ValidationError, DjangoValidationError):
    """Input validation failure raised inside a Django form boundary.

    Represents violations of the expected *shape* of the input data,
    independent of any business rule. Intended to be raised by Django
    forms, Django form fields, and Django model field validators — that
    is, before domain logic runs.

    Mixes in :class:`django.core.exceptions.ValidationError` so that
    Django's form cleaning and admin machinery recognize the instance as
    a native validation failure. At the same time, it remains part of
    the application's :class:`ValidationError` category tree, so
    ``except ValidationError`` catches it.

    May be raised directly with an explicit validation definition
    (typically from :mod:`core.exceptions.errors.validation`), or
    subclassed to bind a concrete ``error_cls`` for a recurring
    scenario.

    Typical scenarios:
        - Missing required field in a form.
        - Invalid format for a model field.
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
        ... from core.exceptions.errors.validation import RequiredField
        ... raise DjangoInputError(RequiredField(field="email"))
        >>>
        >>> # Subclassing to bind a concrete error_cls:
        ... class EmailRequiredError(DjangoInputError):
        ...     error_cls = RequiredField
        ... raise EmailRequiredError(field="email")
    """

    error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.INFO
