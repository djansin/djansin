"""Provides utility functions for user management operations.

This module implements helper functions for generating unique usernames,
identifying identifier types (email/phone), and validating usernames.

IMPORTANT - What these functions do:
    - generate_unique_username: Creates statistically unique usernames for auto-generation
    - is_valid_email / is_valid_phone: Heuristic detection of identifier types (not strict validation)
    - is_valid_identifier: Composite check for any valid identifier type
    - collect_username_errors: Comprehensive username format validation

These are PURE UTILITY functions with no database dependencies. They perform
syntactic validation and detection, not business rule enforcement.
"""

import re
import time
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _t
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException


def generate_unique_username(prefix: str = "user") -> str:
    """Generates a unique username using timestamp and UUID.

    This function creates a username that is highly likely to be unique by
    combining a user-provided prefix with a short UUID fragment and a
    millisecond-precision timestamp.

    Args:
        prefix: The prefix to use for the username. Defaults to "user".

    Returns:
        str: A unique username in the format: {prefix}_{short_uuid}_{timestamp}
            Example: "user_a1b2c3d4e5f6_1735123456789"

    Note:
        This function does not check against existing usernames in the database.
        It only generates a syntactically unique identifier. Callers should
        verify uniqueness against the database if required.
    """
    timestamp = int(time.time() * 1000)
    short_uuid = str(uuid.uuid4()).replace("-", "")[:12]
    username = f"{prefix}_{short_uuid}_{timestamp}"

    return username


def normalize_email(address: str) -> str:
    """Normalizes an email address by lowercasing the domain part.

    This function splits the email address at '@' and lowercases the domain
    portion while preserving the local part case. This follows the common
    convention that domain names are case-insensitive.

    Args:
        address: The email address to normalize.

    Returns:
        str: The normalized email address with lowercase domain,
            or the original if parsing fails.

    Example:
        >>> normalize_email("User@Example.COM")
        ... # "User@example.com"
    """
    address = address or ""
    try:
        email_name, domain_part = address.strip().rsplit("@", 1)
    except ValueError:
        return address
    else:
        return f"{email_name}@{domain_part.lower()}"


def is_valid_email(identifier: str) -> bool:
    """Checks if the identifier appears to be a valid email address.

    Uses Django's built-in email validator to check if the identifier
    conforms to RFC standards for email addresses.

    Args:
        identifier: The string to check.

    Returns:
        bool: True if the identifier is a valid email address,
            False otherwise.
    """
    try:
        validate_email(identifier)
        return True
    except ValidationError:
        return False


def is_valid_normalized_email(address: str) -> bool:
    """Checks if an email address is valid and properly normalized.

    This function validates that the email address is syntactically valid
    and that the domain part is already in lowercase, indicating proper
    normalization.

    Args:
        address: The email address to check.

    Returns:
        bool: True if the email is valid and normalized, False otherwise.

    Example:
        >>> is_valid_normalized_email("User@Example.COM")
        ... # False (domain not normalized)
        >>> is_valid_normalized_email("user@example.com")
        ... # True (valid and normalized)
    """
    if not is_valid_email(address):
        return False
    return address == normalize_email(address)


def is_valid_phone(identifier: str) -> bool:
    """Checks if the identifier appears to be a valid phone number.

    Uses phonenumber library to parse and validate the phone number format.

    Args:
        identifier: The string to check.

    Returns:
        bool: True if the identifier is a valid phone number,
            False otherwise.
    """
    try:
        phone_normalized = PhoneNumber.from_string(identifier)
        return phone_normalized.is_valid()
    except NumberParseException:
        return False


def is_valid_username(username: str, min_length: int = 5, max_length: int = 32) -> bool:
    """Checks if a username is valid according to validation rules.

    Args:
        username: The username string to validate.
        min_length: Minimum allowed length (default: 5).
        max_length: Maximum allowed length (default: 32).

    Returns:
        bool: True if the username passes all validation rules, False otherwise.
    """
    return len(collect_username_errors(username, min_length, max_length)) == 0


def is_valid_identifier(
    identifier: str, min_length: int = 5, max_length: int = 32
) -> bool:
    """Checks if an identifier is valid as any supported type.

    An identifier is considered valid if it matches ANY of:
    - Phone number format (via is_valid_phone)
    - Email address format (via is_valid_email)
    - Username format (via is_valid_username)

    Args:
        identifier: The identifier string to validate.
        min_length: Minimum length for username validation (default: 5).
        max_length: Maximum length for username validation (default: 32).

    Returns:
        bool: True if the identifier is a valid phone, email, or username,
            False otherwise.
    """
    return (
        is_valid_phone(identifier)
        or is_valid_email(identifier)
        or is_valid_username(identifier, min_length, max_length)
    )


def collect_username_errors(
    username: str, min_length: int = 5, max_length: int = 32
) -> list[str]:
    """Collects all validation errors for a username.

    Performs comprehensive validation checks including:
    - Length constraints
    - First character must be alphabetic
    - Allowed characters: lowercase letters, numbers, dot, underscore, hyphen
    - No consecutive special characters (.., --, __)
    - Cannot start or end with dot
    - Cannot start or end with hyphen

    Args:
        username: The username string to validate.
        min_length: Minimum allowed length (default: 5).
        max_length: Maximum allowed length (default: 32).

    Returns:
        list[str]: A list of error messages. Returns an empty list if the
            username passes all validation rules.
    """
    errors = []

    # Length validation
    if len(username) < min_length:
        errors.append(
            _t("Username must be at least %(min_length)d characters long.")
            % {
                "min_length": min_length,
            }
        )

    if len(username) > max_length:
        errors.append(
            _t("Username must be at most %(max_length)d characters long.")
            % {
                "max_length": max_length,
            }
        )

    # Skip further character validation if username is empty
    if not username:
        return errors

    if not username[0].isalpha():
        errors.append(_t("Username must start with an alphabet character (a-z)."))

    # Character validation
    if not re.match(r"^[a-z0-9_.-]+$", username):
        errors.append(
            _t("Username can only contain lowercase letters (a-z), numbers, and . _ -")
        )

    if ".." in username or "--" in username or "__" in username:
        errors.append(
            _t(
                "Username cannot contain consecutive dots (..), hyphens (--), underscores (__)"
            )
        )

    # Start/end with dot validation
    if username.startswith(".") or username.endswith("."):
        errors.append(_t("Username cannot start or end with a dot"))

    if username and (username.startswith("-") or username.endswith("-")):
        errors.append(_t("Username cannot start or end with a hyphen (-)."))

    return errors
