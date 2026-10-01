"""Provides a username validator with comprehensive validation rules.

This module implements a deconstructible UsernameValidator class that validates
usernames against length constraints, character requirements, and format rules.
The validator ensures usernames start with alphabetic characters and only contain
allowed special characters without consecutive or trailing special characters.
"""

from django.utils.deconstruct import deconstructible

from ..exceptions.app import RequiredFieldError, UsernameValidationError
from ..utils.user_identifier import collect_username_errors


@deconstructible
class UsernameValidator:
    """Validator for username fields with configurable length constraints.

    This validator ensures usernames meet specific requirements:
    - Minimum and maximum length constraints
    - Must start with an alphabetic character (a-z)
    - Can only contain lowercase letters, numbers, and the characters . _ -
    - No consecutive dots, hyphens, or underscores
    - Cannot start or end with dots or hyphens

    The validator is deconstructible, making it suitable for use in Django
    model fields and migrations.

    Attributes:
        _min_length: Minimum allowed username length (default: 5).
        _max_length: Maximum allowed username length (default: 32).
    """

    def __init__(
        self,
        min_length: int = 5,
        max_length: int = 32,
    ) -> None:
        """Initializes the UsernameValidator with length constraints.

        Args:
            min_length: Minimum allowed length for usernames. Defaults to 3.
            max_length: Maximum allowed length for usernames. Defaults to 150.
        """
        self._min_length = min_length
        self._max_length = max_length

    def __call__(self, username: str) -> None:
        """Validates the username and raises exceptions on validation failures.

        Args:
            username: The username string to validate.

        Raises:
            RequiredFieldError: If the username is empty or None.
            UsernameValidationError: If the username fails any validation rule.
        """
        if not username:
            raise RequiredFieldError(field="username")

        username = username.strip()
        errors = collect_username_errors(username, self._min_length, self._max_length)

        if errors:
            # Django can handle a list of error messages
            raise UsernameValidationError(field_errors=errors)

    def __eq__(self, other: object) -> bool:
        """Compares two UsernameValidator instances for equality.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if both validators have the same min_length and max_length,
                False otherwise.
        """
        if not isinstance(other, UsernameValidator):
            return NotImplemented
        return (
            self._min_length == other._min_length
            and self._max_length == other._max_length
        )

    def __repr__(self) -> str:
        """Returns a string representation of the UsernameValidator.

        Returns:
            str: A string showing the validator's configured length constraints.
        """
        return f"UsernameValidator(min_length={self._min_length}, max_length={self._max_length})"

    def __hash__(self) -> int:
        """Returns a hash value for the UsernameValidator instance.

        The hash is based on the validator's configuration parameters to ensure
        consistency with __eq__ method. Validators with the same min_length and
        max_length will have the same hash value.

        Returns:
            int: Hash value computed from min_length and max_length attributes.
        """
        return hash((self._min_length, self._max_length))
