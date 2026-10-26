"""Validator package public interface.

This package aggregates the project's validators and their convenience
wrappers under a single import surface. Importing from
``core.validators`` is the supported entry point; the individual
submodules remain importable for advanced use cases (for example,
referencing constants defined on a specific validator).

The exported names fall into two groups:

* Validator classes — subclass :class:`~core.validators.base.BaseValidator`
  and are intended to be instantiated once and reused, optionally
  re-targeted per layer via
  :meth:`~core.validators.base.BaseValidator.for_input` or
  :meth:`~core.validators.base.BaseValidator.for_domain`.
* Convenience functions — module-level callables that build an
  input-layer validator on the fly and run it against a single value.
  Intended for one-off checks and for use in Django's
  ``validators=[...]`` lists.
"""

from .base import BaseValidator
from .birth_date import BirthDateValidator, validate_birth_date
from .national_code import NationalCodeValidator, validate_national_code
from .username import UsernameValidator, validate_username


__all__ = [
    "BaseValidator",
    "BirthDateValidator",
    "validate_birth_date",
    "NationalCodeValidator",
    "validate_national_code",
    "UsernameValidator",
    "validate_username",
]
