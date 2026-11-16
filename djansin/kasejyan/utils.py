"""Utility helpers for the kasejyan application.

This module provides small, dependency-free helpers used across the
kasejyan app. Currently it exposes :func:`generate_six_digit_code`,
a cryptographically secure generator for one-time verification codes.
"""

import secrets


def generate_six_digit_code() -> str:
    """Generate a cryptographically secure six-digit numeric code.

    Produces a uniformly random integer in the inclusive range ``[100000,
    999999]`` using :func:`secrets.randbelow`, guaranteeing a fixed-width
    six-character string with no leading zeros.

    Returns:
        str: A six-character string consisting solely of decimal digits.
    """
    return str(secrets.randbelow(900000) + 100000)
