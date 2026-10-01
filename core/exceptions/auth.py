"""Provides authentication exception classes for security-related errors.

This module defines concrete exception classes that wrap authentication
error definitions. Each exception corresponds to a specific authentication
error scenario and carries an appropriate severity level for monitoring
and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY an authentication error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the auth error looks like" (blueprint)
    - Exception classes (here) = "WHEN the auth error happens" (raised in code flow)
"""

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import AuthError
from core.exceptions.errors.auth import (
    AccountInactive,
    AccountLocked,
    InsufficientPermissions,
    InvalidCredentials,
    InvalidToken,
    TokenExpired,
)


class InvalidTokenError(AuthError):
    """Raised when an authentication token is invalid or expired.

    This exception is typically raised when a request contains an invalid,
    malformed, or expired authentication token. It carries INFO severity
    as token validation failures are expected operational occurrences.

    Common scenarios:
    - Token is malformed or corrupted
    - Token has expired
    - Token signature verification fails

    Attributes:
        _error_cls: The InvalidToken error definition class.
        severity: INFO - normal operational occurrence.
    """

    _error_cls = InvalidToken
    severity = ExceptionSeverity.INFO


class TokenExpiredError(AuthError):
    """Raised when an authentication token has expired.

    This exception is raised when a validly formatted token has passed its
    expiration time. It carries INFO severity as this is a normal operational
    occurrence requiring user re-authentication.

    Common scenarios:
    - Session duration exceeded
    - Token expiration timestamp passed

    Attributes:
        _error_cls: The TokenExpired error definition class.
        severity: INFO - normal operational occurrence.
    """

    _error_cls = TokenExpired
    severity = ExceptionSeverity.INFO


class InsufficientPermissionsError(AuthError):
    """Raised when a user lacks required permissions for an action.

    This exception is raised when an authenticated user attempts an operation
    for which they do not have the necessary permissions. It carries INFO
    severity as this is a common access control occurrence.

    Common scenarios:
    - User lacks required role/permission
    - Resource-specific access check fails
    - RBAC validation fails

    Attributes:
        _error_cls: The InsufficientPermissions error definition class.
        severity: INFO - common access control occurrence.
    """

    _error_cls = InsufficientPermissions
    severity = ExceptionSeverity.INFO


class AccountLockedError(AuthError):
    """Raised when an account is locked due to security policies.

    This exception is raised when a user account has been locked, typically
    after multiple failed authentication attempts or due to administrative
    action. It carries INFO severity as this indicates a security-relevant
    event.

    Common scenarios:
    - Too many failed login attempts
    - Administrative lock placed
    - Security policy violation

    Attributes:
        _error_cls: The AccountLocked error definition class.
        severity: INFO - security-relevant event.
    """

    _error_cls = AccountLocked
    severity = ExceptionSeverity.INFO


class InvalidCredentialsError(AuthError):
    """Raised when authentication credentials are invalid.

    This exception is raised when provided credentials (e.g., username/password)
    are incorrect or do not match any known user. It carries INFO severity as
    this is a common, expected occurrence during normal operation.

    Common scenarios:
    - Username not found
    - Password does not match
    - Combined credential verification fails

    Attributes:
        _error_cls: The InvalidCredentials error definition class.
        severity: INFO - common expected occurrence.
    """

    _error_cls = InvalidCredentials
    severity = ExceptionSeverity.INFO


class AccountInactiveError(AuthError):
    """Raised when a user account is inactive.

    This exception is raised when an authentication attempt is made with a
    user account that exists but is marked as inactive (is_active=False).
    It carries INFO severity as this indicates a disabled account.

    Common scenarios:
    - Account pending activation
    - Account suspended by admin
    - Account disabled due to policy

    Attributes:
        _error_cls: The AccountInactive error definition class.
        severity: INFO - disabled account indication.
    """

    _error_cls = AccountInactive
    severity = ExceptionSeverity.INFO
