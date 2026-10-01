"""Provides HTTP exception classes for common HTTP protocol violations.

This module defines concrete exception classes that wrap HTTP error
definitions. Each exception corresponds to a specific HTTP error scenario
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY an HTTP error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the HTTP error looks like" (blueprint)
    - Exception classes (here) = "WHEN the HTTP error happens" (raised in code flow)
"""

from typing import overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import HttpError
from core.exceptions.errors.common import HttpErrorDefinition
from core.exceptions.errors.http import (
    BadRequest,
    Conflict,
    Forbidden,
    MethodNotAllowed,
    NotAcceptable,
    NotFound,
    RateLimited,
    Unauthorized,
)


class HttpNotFoundError(HttpError):
    """Raised when a requested resource cannot be found (404).

    This exception is raised when a client requests a resource that does not
    exist at the specified URL or identifier.

    Common scenarios:
    - API endpoint with non-existent resource ID
    - Page or route that doesn't exist
    - Deleted resource that was previously accessible
    - Invalid URL path

    This error is NOT retryable as the resource doesn't exist.

    Attributes:
        _error_cls: The NotFound error definition class.
        severity: INFO - normal client errors.
    """

    _error_cls = NotFound
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        resource: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes a not found exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class BadRequestError(HttpError):
    """Raised when a request is malformed or invalid (400).

    This exception is raised for malformed or invalid HTTP requests such as
    syntax errors, missing parameters, or invalid JSON.

    Common scenarios:
    - Invalid JSON payload
    - Missing required query parameters
    - Malformed request headers
    - Invalid content type
    - Request entity too large

    This error is NOT retryable as the client must fix the request.

    Attributes:
        _error_cls: The BadRequest error definition class.
        severity: INFO - normal client errors.
    """

    _error_cls = BadRequest
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes a bad request exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class UnauthorizedError(HttpError):
    """Raised when authentication is required but not provided or invalid (401).

    This exception is raised when a request lacks valid authentication
    credentials or the provided credentials are invalid.

    Common scenarios:
    - Missing authentication token
    - Expired or invalid API key
    - Invalid session cookie
    - Missing or invalid Basic Auth credentials

    This error is NOT retryable as the client must provide valid credentials.

    Attributes:
        _error_cls: The Unauthorized error definition class.
        severity: INFO - normal authentication failures.
    """

    _error_cls = Unauthorized
    severity = ExceptionSeverity.INFO


class ForbiddenError(HttpError):
    """Raised when an authenticated user lacks access to a resource (403).

    This exception is raised when an authenticated user does not have the
    necessary permissions to access a resource or perform an action.

    Common scenarios:
    - User lacks required role or permission
    - Resource-specific access control denies access
    - IP address or location restrictions
    - Account type doesn't have access to feature

    This error is NOT retryable as permissions won't change on retry.

    Attributes:
        _error_cls: The Forbidden error definition class.
        severity: INFO - normal authorization failures.
    """

    _error_cls = Forbidden
    severity = ExceptionSeverity.INFO


class MethodNotAllowedError(HttpError):
    """Raised when an HTTP method is not supported for the endpoint (405).

    This exception is raised when a client uses an HTTP method that is not
    supported by the requested endpoint.

    Common scenarios:
    - POST request to a read-only endpoint
    - DELETE request to a resource that doesn't support deletion
    - PUT request when only PATCH is supported
    - GET request to a write-only endpoint

    This error is NOT retryable as the client must change the HTTP method.

    Attributes:
        _error_cls: The MethodNotAllowed error definition class.
        severity: INFO - normal client mistakes.
    """

    _error_cls = MethodNotAllowed
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        method: str | None = None,
        allowed_methods: list[str] | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes a method not allowed exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class HttpRateLimitedError(HttpError):
    """Raised when a client has exceeded the allowed request rate (429).

    This exception is raised when a client has made too many requests within
    a given time window and has been rate limited.

    Common scenarios:
    - API rate limit exceeded
    - Login attempt rate limiting
    - Search request throttling
    - Bulk operation limits exceeded

    This error IS retryable after waiting the specified period.

    Attributes:
        _error_cls: The RateLimited error definition class.
        severity: INFO - normal traffic management mechanism.
    """

    _error_cls = RateLimited
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        retry_after: int | None = None,
        unit: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes an HTTP rate limited exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class NotAcceptableError(HttpError):
    """Raised when the requested content type cannot be provided (406).

    This exception is raised when the server cannot provide a response in
    a content type that is acceptable to the client.

    Common scenarios:
    - Client requests JSON but server only supports XML
    - Unsupported Accept header value
    - Content negotiation failure
    - Unsupported media type for response

    This error is NOT retryable as the client must change Accept headers.

    Attributes:
        _error_cls: The NotAcceptable error definition class.
        severity: INFO - normal content negotiation issues.
    """

    _error_cls = NotAcceptable
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes a not acceptable exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class ConflictError(HttpError):
    """Raised when a request conflicts with the current state of the resource (409).

    This exception is raised when a request cannot be completed due to a
    conflict with the current state of the target resource.

    Common scenarios:
    - Optimistic locking version mismatch
    - Resource already exists with unique identifier
    - Resource state transition conflict
    - Concurrent modification detected
    - Dependency conflict in composite operations

    This error is NOT retryable as the client must resolve the conflict.

    Attributes:
        _error_cls: The Conflict error definition class.
        severity: INFO - normal concurrency issues.
    """

    _error_cls = Conflict
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | HttpErrorDefinition | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | HttpErrorDefinition | None = None, /, **kwds):
        """Initializes a conflict exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
