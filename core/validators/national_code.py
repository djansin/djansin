"""Iranian national code validator and convenience validation function.

This module provides :class:`NationalCodeValidator`, a concrete
:class:`~core.validators.base.Validator` that validates Iranian
national codes using the standard checksum algorithm. A
module-level :func:`validate_national_code` helper wraps the validator
for one-off, input-layer usage.
"""

from typing import Any

from django.utils.translation import gettext_lazy as _t

from core.exceptions.errors.validation import InvalidFormat
from core.validators.base import Validator


class NationalCodeValidator(Validator):
    """Validate an Iranian national code.

    A value passes validation when, after string conversion and stripping,
    it satisfies all of the following:

    1. It is exactly 10 characters long.
    2. It consists only of digits.
    3. It is not composed of a single repeated digit.
    4. Its check digit (the 10th digit) matches the value derived from the
       standard weighted checksum algorithm (mod 11).

    Blank handling is inherited from :class:`Validator`. ``None`` and
    the empty string are also short-circuited locally, deferring blank
    handling to the caller (for example, a model field).

    Example:
        >>> NationalCodeValidator().run("0499370899")
        '0499370899'
    """

    def validate(self, value) -> None:
        """Validate a national code.

        Args:
            value: The value to validate. ``None`` and ``""`` are accepted
                silently, deferring blank handling to the caller. Any other
                value is coerced to ``str`` and stripped before checking.

        Raises:
            InvalidFormat: If the value fails the length, digit-only,
                non-repeated, or checksum checks.
        """
        if value in (None, ""):
            return  # blank handled by the model field

        value = str(value).strip()

        # --- 1) Length ---
        if len(value) != 10:
            self.raise_validation_error(
                InvalidFormat(_t("National code must be exactly 10 digits."))
            )

        # --- 2) Digits only ---
        if not value.isdigit():
            self.raise_validation_error(
                InvalidFormat(_t("National code must contain only digits."))
            )

        # --- 3) Not all identical digits ---
        if len(set(value)) == 1:
            self.raise_validation_error(
                InvalidFormat(_t("National code cannot consist of identical digits."))
            )

        # --- 4) Checksum ---
        check = int(value[9])
        total = sum(int(value[i]) * (10 - i) for i in range(9))
        remainder = total % 11

        expected = remainder if remainder < 2 else 11 - remainder

        if expected != check:
            self.raise_validation_error(
                InvalidFormat(_t("National code is not valid."))
            )


def validate_national_code(
    value: Any, /, *, allow_blank: bool = True, trim: bool = True
) -> str | None:
    """Validate an Iranian national code using an input-layer validator.

    Convenience wrapper around :class:`NationalCodeValidator` that builds a
    validator configured with
    :meth:`~core.validators.base.Validator.for_input` and runs it
    against ``value``. Intended for one-off checks where holding onto a
    validator instance is unnecessary.

    Args:
        value (Any): The national code to validate.
        allow_blank (bool): If ``True``, blank values pass through without
            validation. Defaults to ``True``.
        trim (bool): If ``True``, surrounding whitespace is stripped from
            string values during normalization. Defaults to ``True``.

    Returns:
        str | None: The validated national code, or ``None`` if ``value`` was
            blank and ``allow_blank`` is ``True``.

    Raises:
        DrfInputError: If the value fails validation.
    """
    validator = NationalCodeValidator(allow_blank=allow_blank, trim=trim).for_input()

    return validator.run(value=value)
