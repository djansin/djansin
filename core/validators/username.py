"""Username validator and convenience validation function.

This module provides :class:`UsernameValidator`, a concrete
:class:`~core.validators.base.BaseValidator` that validates usernames
using a configurable length range and a shared error-collection utility.
A module-level :func:`validate_username` helper wraps the validator for
one-off, input-layer usage.
"""

from collections.abc import Callable
from typing import Any

from django.utils.translation import gettext_lazy as _t

from core.exceptions import AppError, ValidationError
from core.exceptions.errors.app import InvalidValue
from core.exceptions.errors.validation import InvalidUsername
from core.utils.user_identifier import collect_username_errors
from core.validators.base import BaseValidator


class UsernameValidator(BaseValidator):
    """Validate a username against configurable length constraints.

    The actual validation rules are delegated to
    :func:`~core.utils.user_identifier.collect_username_errors`, which
    returns a collection of field-level errors. If that collection is
    non-empty, an :class:`~core.exceptions.errors.validation.InvalidUsername`
    is raised with the collected errors attached.

    Blank handling is inherited from :class:`BaseValidator`; blank values
    are short-circuited in :meth:`~core.validators.base.BaseValidator.run`
    when ``allow_blank`` is ``True``.

    Args:
        min_length (int): Minimum acceptable username length. Must be
            non-negative. Defaults to ``5``.
        max_length (int): Maximum acceptable username length. Must be
            greater than or equal to ``min_length``. Defaults to ``32``.
        allow_blank (bool): If ``True``, blank values pass through without
            validation. Defaults to ``True``.
        error_factory (Callable[..., ValidationError] | None): Factory used
            to build validation errors. Defaults to ``None``, deferring to
            the base class default.

    Raises:
        AppError: If ``min_length`` is negative, or if ``max_length`` is
            less than ``min_length``.

    Example:
        >>> UsernameValidator().run("alice")
        'alice'
    """

    def __init__(
        self,
        min_length: int = 5,
        max_length: int = 32,
        allow_blank: bool = True,
        error_factory: Callable[..., ValidationError] | None = None,
    ) -> None:
        """Initialize the validator and validate its configuration.

        Args:
            min_length (int): Minimum acceptable username length. Must be
                non-negative. Defaults to ``5``.
            max_length (int): Maximum acceptable username length. Must be
                greater than or equal to ``min_length``. Defaults to ``32``.
            allow_blank (bool): If ``True``, blank values pass through
                without validation. Defaults to ``True``.
            error_factory (Callable[..., ValidationError] | None): Factory
                used to build validation errors. Defaults to ``None``.

        Raises:
            AppError: If ``min_length`` is negative, or if ``max_length``
                is less than ``min_length``.
        """
        if min_length < 0:
            raise AppError(InvalidValue(_t("min_length must be non-negative.")))
        if max_length < min_length:
            raise AppError(
                InvalidValue(
                    _t("max_length must be greater than or equal to min_length.")
                )
            )

        self._min_length = min_length
        self._max_length = max_length

        super().__init__(
            min_length=min_length,
            max_length=max_length,
            allow_blank=allow_blank,
            error_factory=error_factory,
        )

    def validate(self, value: Any) -> None:
        """Validate a username.

        Delegates rule evaluation to
        :func:`~core.utils.user_identifier.collect_username_errors`. If any
        errors are collected, raises a single
        :class:`~core.exceptions.errors.validation.InvalidUsername` carrying
        all of them.

        Blank handling is intentionally left to
        :meth:`~core.validators.base.BaseValidator.run`. This method assumes
        the value is non-blank (or that ``allow_blank`` is ``False`` and the
        caller accepts that blank values will be validated here).

        Args:
            value (Any): The value to validate.

        Raises:
            InvalidUsername: If the collected username errors are
                non-empty.
        """
        errors = collect_username_errors(value, self._min_length, self._max_length)

        if errors:
            self.raise_validation_error(InvalidUsername(field_errors=errors))


def validate_username(
    value: Any,
    /,
    *,
    min_length: int = 5,
    max_length: int = 32,
    allow_blank: bool = True,
) -> str | None:
    """Validate a username using an input-layer validator.

    Convenience wrapper around :class:`UsernameValidator` that builds a
    validator configured with
    :meth:`~core.validators.base.BaseValidator.for_input` and runs it
    against ``value``. Intended for one-off checks where holding onto a
    validator instance is unnecessary.

    Args:
        value (Any): The username to validate.
        min_length (int): Minimum acceptable username length. Defaults to
            ``5``.
        max_length (int): Maximum acceptable username length. Defaults to
            ``32``.
        allow_blank (bool): If ``True``, blank values pass through without
            validation. Defaults to ``True``.

    Returns:
        str | None: The validated username, or ``None`` if ``value`` was
            blank and ``allow_blank`` is ``True``.

    Raises:
        AppError: If the validator configuration is invalid (for example,
            ``min_length`` is negative).
        DrfInputError: If the value fails validation.
    """
    validator = UsernameValidator(
        min_length=min_length,
        max_length=max_length,
        allow_blank=allow_blank,
    ).for_input()

    return validator.run(value=value)
