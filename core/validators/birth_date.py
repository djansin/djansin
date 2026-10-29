"""Birth date validator and convenience validation function.

This module provides :class:`BirthDateValidator`, a concrete
:class:`~core.validators.base.Validator` that checks a value is a
valid date, is not in the future, and yields an age within a configurable
range. A module-level :func:`validate_birth_date` helper wraps the
validator for one-off, input-layer usage.
"""

from collections.abc import Callable
from datetime import date
from typing import Any

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import AppError, ValidationError
from core.exceptions.errors.app import InvalidValue
from core.exceptions.errors.validation import InvalidFormat
from core.utils.date_utils import compute_age
from core.validators.base import Validator


class BirthDateValidator(Validator):
    """Validate that a value is a birth date within an allowed age range.

    A value passes validation when it is a :class:`datetime.date`, is not
    in the future relative to the reference date, and corresponds to an age
    between ``min_age`` and ``max_age`` (inclusive).

    Blank handling is inherited from :class:`Validator`: when
    ``allow_blank`` is ``True``, blank values bypass validation entirely.

    Args:
        min_age (int): Minimum acceptable age in years. Must be
            non-negative. Defaults to ``18``.
        max_age (int): Maximum acceptable age in years. Must be greater
            than or equal to ``min_age``. Defaults to ``120``.
        reference_date (date | None): Date used as "today" when computing
            age. Defaults to ``None``, in which case the current date is
            used.
        allow_blank (bool): If ``True``, blank values pass through without
            validation. Defaults to ``True``.
        error_factory (Callable[..., Exception] | None): Factory used to
            build validation errors. Defaults to ``None``, deferring to the
            base class default.

    Raises:
        AppError: If ``min_age`` is negative, or if ``max_age`` is less
            than ``min_age``.

    Example:
        >>> validator = BirthDateValidator(min_age=18, max_age=65)
        >>> validator.run(date(1990, 5, 1))
        datetime.date(1990, 5, 1)
    """

    def __init__(
        self,
        min_age: int = 18,
        max_age: int = 120,
        reference_date: date | None = None,
        allow_blank: bool = True,
        error_factory: Callable[..., ValidationError] | None = None,
    ) -> None:
        """Initialize the validator and validate its configuration.

        Args:
            min_age (int): Minimum acceptable age in years. Must be
                non-negative. Defaults to ``18``.
            max_age (int): Maximum acceptable age in years. Must be greater
                than or equal to ``min_age``. Defaults to ``120``.
            reference_date (date | None): Date used as "today" when
                computing age. Defaults to ``None``.
            allow_blank (bool): If ``True``, blank values pass through
                without validation. Defaults to ``True``.
            error_factory (Callable[..., Exception] | None): Factory used
                to build validation errors. Defaults to ``None``.

        Raises:
            AppError: If ``min_age`` is negative, or if ``max_age`` is less
                than ``min_age``.
        """
        if min_age < 0:
            raise AppError(InvalidValue(_t("min_age must be non-negative.")))
        if max_age < min_age:
            raise AppError(
                InvalidValue(_t("max_age must be greater than or equal to min_age."))
            )

        self._min_age = min_age
        self._max_age = max_age
        self._reference_date = reference_date

        super().__init__(
            min_age=min_age,
            max_age=max_age,
            reference_date=reference_date,
            allow_blank=allow_blank,
            error_factory=error_factory,
        )

    @property
    def _today(self) -> timezone.datetime:
        """date: The reference date used for age computation.

        Falls back to the current date when no explicit reference date was
        provided at construction time.
        """
        return self._reference_date or timezone.datetime.today()

    def validate(self, value: Any) -> None:
        """Validate a birth date against the configured age range.

        The value must be a :class:`datetime.date`, must not be in the
        future relative to :attr:`_today`, and must yield an age within
        ``[min_age, max_age]``.

        Args:
            value (Any): The value to validate. ``None`` is accepted
                silently, deferring blank handling to the caller.

        Raises:
            InvalidFormat: If the value is not a date, is in the future, or
                falls outside the allowed age range.
        """
        if value is None:
            return  # blank handled by the caller

        if not isinstance(value, date):
            self.raise_validation_error(
                InvalidFormat(_t("Birth date must be a valid date."))
            )

        if value > self._today:
            self.raise_validation_error(
                InvalidFormat(_t("Birth date cannot be in the future."))
            )

        age = compute_age(
            timezone.datetime(value.year, value.month, value.day), self._today()
        )

        if age < self._min_age:
            self.raise_validation_error(
                InvalidFormat(
                    _t("Age must be at least %(min_age)d years."), min_age=self._min_age
                )
            )

        if age > self._max_age:
            self.raise_validation_error(
                InvalidFormat(
                    _t("Age must be at most %(max_age)d years."), max_age=self._max_age
                )
            )


def validate_birth_date(
    value: Any,
    /,
    *,
    min_age: int = 18,
    max_age: int = 120,
    reference_date: date | None = None,
    allow_blank: bool = True,
) -> date | None:
    """Validate a birth date using an input-layer validator.

    Convenience wrapper around :class:`BirthDateValidator` that builds a
    validator configured with :meth:`~core.validators.base.Validator.for_input`
    and runs it against ``value``. Intended for one-off checks where
    holding onto a validator instance is unnecessary.

    Args:
        value (Any): The birth date to validate.
        min_age (int): Minimum acceptable age in years. Defaults to ``18``.
        max_age (int): Maximum acceptable age in years. Defaults to ``120``.
        reference_date (date | None): Date used as "today" when computing
            age. Defaults to ``None``.
        allow_blank (bool): If ``True``, blank values pass through without
            validation. Defaults to ``True``.

    Returns:
        date | None: The validated birth date, or ``None`` if ``value`` was
            blank and ``allow_blank`` is ``True``.

    Raises:
        AppError: If the validator configuration is invalid (for example,
            ``min_age`` is negative).
        DrfInputError: If the value fails validation.
    """
    validator = BirthDateValidator(
        min_age=min_age,
        max_age=max_age,
        reference_date=reference_date,
        allow_blank=allow_blank,
    ).for_input()
    return validator.run(value=value)
