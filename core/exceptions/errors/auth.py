"""Provides authentication and authorization error definitions for security-related violations.

This module defines concrete error definition classes for authentication and
authorization-related errors including invalid tokens, expired sessions,
insufficient permissions, locked accounts, invalid credentials, inactive
accounts, permission denials, authentication failures, and missing credentials.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW an authentication error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like AuthenticationFailed) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the auth error looks like" (blueprint)
    - Exception classes = "WHEN the auth error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import AuthErrorDefinition


class InvalidToken(AuthErrorDefinition):
    """Error definition for invalid or malformed authentication tokens.

    This error occurs when a provided authentication token is invalid,
    malformed, or cannot be properly decoded or verified.

    Attributes:
        code: "AUTH:INVALID_TOKEN"
        http_status: 401 Unauthorized
        message_template: "Invalid or expired token. Please authenticate again."
        is_retryable: False (requires new authentication)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(InvalidToken())
    """

    code = "AUTH:INVALID_TOKEN"
    http_status = 401
    message_template = _n("Invalid or expired token. Please authenticate again.")
    is_retryable = False


class TokenExpired(AuthErrorDefinition):
    """Error definition for expired authentication tokens.

    This error occurs when a provided authentication token has exceeded
    its validity period and can no longer be used for authentication.

    Attributes:
        code: "AUTH:TOKEN_EXPIRED"
        http_status: 401 Unauthorized
        message_template: "Your session has expired. Please log in again."
        is_retryable: False (requires new authentication)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(TokenExpired())
    """

    code = "AUTH:TOKEN_EXPIRED"
    http_status = 401
    message_template = _n("Your session has expired. Please log in again.")
    is_retryable = False


class InsufficientPermissions(AuthErrorDefinition):
    """Error definition for users lacking required permissions.

    This error occurs when an authenticated user attempts to perform an
    action that requires permissions they do not possess.

    Attributes:
        code: "AUTH:INSUFFICIENT_PERMISSIONS"
        http_status: 403 Forbidden
        message_template: "You don't have permission to perform this action."
        is_retryable: False (requires permission upgrade)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(InsufficientPermissions())
    """

    code = "AUTH:INSUFFICIENT_PERMISSIONS"
    http_status = 403
    message_template = _n("You don't have permission to perform this action.")
    is_retryable = False


class AccountLocked(AuthErrorDefinition):
    """Error definition for locked user accounts.

    This error occurs when a user account has been temporarily or permanently
    locked due to multiple failed authentication attempts or security policies.

    Attributes:
        code: "AUTH:ACCOUNT_LOCKED"
        http_status: 403 Forbidden
        message_template: "Your account has been locked due to multiple failed attempts."
        is_retryable: False (requires manual unlock or timeout)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(AccountLocked())
    """

    code = "AUTH:ACCOUNT_LOCKED"
    http_status = 403
    message_template = _n(
        "Your account has been locked due to multiple failed attempts."
    )
    is_retryable = False


class InvalidCredentials(AuthErrorDefinition):
    """Error definition for invalid authentication credentials.

    This error occurs when a user provides incorrect login credentials
    such as a wrong password or non-existent username.

    Attributes:
        code: "AUTH:INVALID_CREDENTIALS"
        http_status: 401 Unauthorized
        message_template: "Invalid login identifier or password."
        is_retryable: False (requires valid credentials)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(InvalidCredentials())
    """

    code = "AUTH:INVALID_CREDENTIALS"
    http_status = 401
    message_template = _n("Invalid login identifier or password.")
    is_retryable = False


class AccountInactive(AuthErrorDefinition):
    """Error definition for inactive user accounts.

    This error occurs when a user attempts to authenticate with an account
    that has been deactivated or marked as inactive.

    Attributes:
        code: "AUTH:ACCOUNT_INACTIVE"
        http_status: 403 Forbidden
        message_template: "Your account is inactive. Please contact support to activate your account."
        is_retryable: False (requires administrative action)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(AccountInactive())
    """

    code = "AUTH:ACCOUNT_INACTIVE"
    http_status = 403
    message_template = _n(
        "Your account is inactive. Please contact support to activate your account."
    )
    is_retryable = False


class PermissionDenied(AuthErrorDefinition):
    """Error definition for specific permission violations.

    This error occurs when an authenticated user attempts to perform an
    action that is explicitly forbidden, often with additional context
    about why the permission was denied.

    Attributes:
        code: "AUTH:PERMISSION_DENIED"
        http_status: 403 Forbidden
        message_template: "You do not have permission to perform this action. {detail}"
        is_retryable: False (requires permission grant)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(PermissionDenied(detail="Resource is owned by another user"))
    """

    code = "AUTH:PERMISSION_DENIED"
    http_status = 403
    message_template = _n("You do not have permission to perform this action. {detail}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        detail: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a permission denied error definition.

        Args:
            message_template: Optional custom message template override.
            **kwds: Additional context values for message formatting.
        """
        super().__init__(message_template, **kwds)


class AuthenticationFailed(AuthErrorDefinition):
    """Error definition for general authentication failures.

    This error occurs when the authentication process fails for various
    reasons including invalid credentials, unsupported authentication
    methods, or internal authentication errors.

    Attributes:
        code: "AUTH:AUTHENTICATION_FAILED"
        http_status: 401 Unauthorized
        message_template: "Authentication failed. {detail}"
        is_retryable: False (requires valid authentication method)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(AuthenticationFailed(detail="Invalid API key format"))
    """

    code = "AUTH:AUTHENTICATION_FAILED"
    http_status = 401
    message_template = _n("Authentication failed. {detail}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        detail: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an authentication failed error definition.

        Args:
            message_template: Optional custom message template override.
            **kwds: Additional context values for message formatting.
        """
        super().__init__(message_template, **kwds)


class NotAuthenticated(AuthErrorDefinition):
    """Error definition for missing authentication credentials.

    This error occurs when a request is made to a protected endpoint
    without providing any authentication credentials.

    Attributes:
        code: "AUTH:NOT_AUTHENTICATED"
        http_status: 401 Unauthorized
        message_template: "Authentication credentials were not provided."
        is_retryable: False (requires valid credentials)

    Example:
        >>> # Wrap this definition in an authentication-specific exception
        ... raise AuthError(NotAuthenticated())
    """

    code = "AUTH:NOT_AUTHENTICATED"
    http_status = 401
    message_template = _n("Authentication credentials were not provided.")
    is_retryable = False
