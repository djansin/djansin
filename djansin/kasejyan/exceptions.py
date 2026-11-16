"""Domain-specific error definitions for the authentication application.

This module declares concrete :class:`~core.exceptions.errors.ValidErrorDefinition`
subclasses that describe authentication-related failure conditions in a
structured, machine-readable form. Each definition carries a stable error
code, an HTTP status, a translatable message template, and a retryability
hint, allowing services and serializers to raise consistent errors across
the API.
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors import ValidErrorDefinition


class InvalidVerificationCode(ValidErrorDefinition):
    """Error raised when a verification code fails validation.

    Represents the case where a one-time verification code is missing,
    expired, exhausted, or does not match the stored value. The message
    interpolates the ``target`` label (e.g. ``"email address"`` or
    ``"phone number"``) to indicate which contact failed verification.

    Attributes:
        code (str): Stable error identifier
            (``"VALID:INVALID_VERIFICATION_CODE"``).
        http_status (int): HTTP status returned to the client (``422``).
        message_template (str): Translatable message template containing a
            ``{target}`` placeholder.
        is_retryable (bool): Whether the operation may be retried as-is
            (``False``).
    """

    code = "VALID:INVALID_VERIFICATION_CODE"
    http_status = 422
    message_template = _n("The verification code sent to your {target} is invalid.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        target: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initialize the error with an optional message override.

        Args:
            message_template (str | None, optional): A custom message
                template overriding the class default. Defaults to
                ``None``.
            **kwds: Template interpolation values (e.g. ``target``).
        """
        super().__init__(message_template, **kwds)


class InvalidIdentifier(ValidErrorDefinition):
    """Error raised when an identifier does not match any supported format.

    Represents the case where a supplied identifier is neither a valid
    email address nor a valid phone number. The message interpolates the
    offending value via the ``{identifier}`` placeholder.

    Attributes:
        code (str): Stable error identifier
            (``"VALID:INVALID_IDENTIFIER"``).
        http_status (int): HTTP status returned to the client (``422``).
        message_template (str): Translatable message template containing an
            ``{identifier}`` placeholder.
        is_retryable (bool): Whether the operation may be retried as-is
            (``False``).
    """

    code = "VALID:INVALID_IDENTIFIER"
    http_status = 422
    message_template = _n("Identifier '{identifier}' is not valid.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        identifier: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initialize the error with an optional message override.

        Args:
            message_template (str | None, optional): A custom message
                template overriding the class default. Defaults to
                ``None``.
            **kwds: Template interpolation values (e.g. ``identifier``).
        """
        super().__init__(message_template, **kwds)


class InvalidLoginIdentifier(ValidErrorDefinition):
    """Error raised when login credentials do not resolve to a user.

    Represents a generic authentication failure surfaced when the supplied
    identifier, password, or verification code combination is invalid.
    The message is intentionally non-specific to avoid leaking whether an
    account exists.

    Attributes:
        code (str): Stable error identifier
            (``"VALID:INVALID_LOGIN_IDENTIFIER"``).
        http_status (int): HTTP status returned to the client (``422``).
        message_template (str): Translatable, generic message template.
        is_retryable (bool): Whether the operation may be retried as-is
            (``False``).
    """

    code = "VALID:INVALID_LOGIN_IDENTIFIER"
    http_status = 422
    message_template = _n("The login information you provided is incorrect.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initialize the error with an optional message override.

        Args:
            message_template (str | None, optional): A custom message
                template overriding the class default. Defaults to
                ``None``.
            **kwds: Additional template interpolation values.
        """
        super().__init__(message_template, **kwds)
