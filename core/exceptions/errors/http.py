"""Provides HTTP error definitions for common HTTP protocol violations.

This module defines concrete error definition classes for HTTP-related
errors including not found, bad requests, unauthorized access, forbidden
access, method not allowed, rate limiting, conflicts, unsupported media
types, parsing errors, suspicious operations, size limit violations,
and host resolution errors.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW an HTTP error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like HttpError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the HTTP error looks like" (blueprint)
    - Exception classes = "WHEN the HTTP error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import HttpErrorDefinition


class NotFound(HttpErrorDefinition):
    """Error definition for resource not found.

    This error occurs when a requested resource cannot be found on the server.

    Attributes:
        code: "HTTP:NOT_FOUND"
        http_status: 404 Not Found
        message_template: "The requested {resource} was not found."
        is_retryable: False (resource doesn't exist)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(NotFound(resource="Product"))
    """

    code = "HTTP:NOT_FOUND"
    http_status = 404
    message_template = _n("The requested {resource} was not found.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        resource: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a not found error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class BadRequest(HttpErrorDefinition):
    """Error definition for malformed or invalid HTTP requests.

    This error occurs when the server cannot process the request due to
    client-side errors such as malformed syntax, invalid parameters,
    or missing required data.

    Attributes:
        code: "HTTP:BAD_REQUEST"
        http_status: 400 Bad Request
        message_template: "Invalid request. {details}"
        is_retryable: False (requires request correction)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(BadRequest(details="Missing required field: email"))
    """

    code = "HTTP:BAD_REQUEST"
    http_status = 400
    message_template = _n("Invalid request. {details}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a bad request error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Unauthorized(HttpErrorDefinition):
    """Error definition for missing authentication credentials.

    This error occurs when a request is made to a protected resource
    without providing valid authentication credentials.

    Attributes:
        code: "HTTP:UNAUTHORIZED"
        http_status: 401 Unauthorized
        message_template: "Authentication required."
        is_retryable: False (requires valid credentials)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(Unauthorized())
    """

    code = "HTTP:UNAUTHORIZED"
    http_status = 401
    message_template = _n("Authentication required.")
    is_retryable = False


class Forbidden(HttpErrorDefinition):
    """Error definition for insufficient permissions.

    This error occurs when an authenticated user attempts to access
    a resource they do not have permission to access.

    Attributes:
        code: "HTTP:FORBIDDEN"
        http_status: 403 Forbidden
        message_template: "Access denied."
        is_retryable: False (requires permission grant)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(Forbidden())
    """

    code = "HTTP:FORBIDDEN"
    http_status = 403
    message_template = _n("Access denied.")
    is_retryable = False


class MethodNotAllowed(HttpErrorDefinition):
    """Error definition for unsupported HTTP methods.

    This error occurs when a request uses an HTTP method that is not
    supported by the endpoint.

    Attributes:
        code: "HTTP:METHOD_NOT_ALLOWED"
        http_status: 405 Method Not Allowed
        message_template: "Method '{method}' not allowed."
        is_retryable: False (requires different HTTP method)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(MethodNotAllowed(method="DELETE"))
    """

    code = "HTTP:METHOD_NOT_ALLOWED"
    http_status = 405
    message_template = _n("Method '{method}' not allowed.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        method: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a method not allowed error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class RateLimited(HttpErrorDefinition):
    """Error definition for rate limit exceedances.

    This error occurs when a client exceeds the allowed request rate.
    The operation can be retried after the specified waiting period.

    Attributes:
        code: "HTTP:RATE_LIMITED"
        http_status: 429 Too Many Requests
        message_template: "Too many requests. Please try again in {retry_after} {unit}."
        is_retryable: True (can retry after waiting)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(RateLimited(retry_after=30, unit="seconds"))
    """

    code = "HTTP:RATE_LIMITED"
    http_status = 429
    message_template = _n(
        "Too many requests. Please try again in {retry_after} {unit}."
    )
    is_retryable = True

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        retry_after: int | None = None,
        unit: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an HTTP rate limited error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class NotAcceptable(HttpErrorDefinition):
    """Error definition for unsupported content types.

    This error occurs when the server cannot generate content that matches
    the Accept headers sent by the client.

    Attributes:
        code: "HTTP:NOT_ACCEPTABLE"
        http_status: 406 Not Acceptable
        message_template: "Request not acceptable. {details}"
        is_retryable: False (requires different Accept header)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(NotAcceptable(
        ...     details="Server only supports application/json"
        ... ))
    """

    code = "HTTP:NOT_ACCEPTABLE"
    http_status = 406
    message_template = _n("Request not acceptable. {details}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a not acceptable error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Conflict(HttpErrorDefinition):
    """Error definition for resource conflicts.

    This error occurs when a request conflicts with the current state
    of the resource, such as concurrent modifications or version mismatches.

    Attributes:
        code: "HTTP:CONFLICT"
        http_status: 409 Conflict
        message_template: "Resource conflict. {details}"
        is_retryable: False (requires manual resolution)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(Conflict(
        ...     details="Resource was modified by another user"
        ... ))
    """

    code = "HTTP:CONFLICT"
    http_status = 409
    message_template = _n("Resource conflict. {details}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a conflict error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class UnsupportedMediaType(HttpErrorDefinition):
    """Error definition for unsupported media types in requests.

    This error occurs when the request's Content-Type header specifies
    a media type that is not supported by the server.

    Attributes:
        code: "HTTP:UNSUPPORTED_MEDIA_TYPE"
        http_status: 415 Unsupported Media Type
        message_template: "Unsupported media type '{media_type}' in request."
        is_retryable: False (requires different Content-Type)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(UnsupportedMediaType(media_type="application/xml"))
    """

    code = "HTTP:UNSUPPORTED_MEDIA_TYPE"
    http_status = 415
    message_template = _n("Unsupported media type '{media_type}' in request.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        media_type: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an unsupported media type error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ParserError(HttpErrorDefinition):
    """Error definition for malformed request data parsing.

    This error occurs when the request data cannot be parsed due to
    malformed JSON, invalid XML, or other data format issues.

    Attributes:
        code: "HTTP:PARSE_ERROR"
        http_status: 400 Bad Request
        message_template: "Malformed request. {detail}"
        is_retryable: False (requires data format correction)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(ParserError(detail="Invalid JSON at line 5"))
    """

    code = "HTTP:PARSE_ERROR"
    http_status = 400
    message_template = _n("Malformed request. {detail}")
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
        """Initializes a parser error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class SuspiciousOperation(HttpErrorDefinition):
    """Error definition for suspicious HTTP operations.

    This error occurs when the request exhibits suspicious patterns
    that could indicate security threats or malicious intent.

    Attributes:
        code: "HTTP:SUSPICIOUS_OPERATION"
        http_status: 400 Bad Request
        message_template: "Suspicious operation detected. {detail}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(SuspiciousOperation(
        ...     detail="SQL injection pattern detected"
        ... ))
    """

    code = "HTTP:SUSPICIOUS_OPERATION"
    http_status = 400
    message_template = _n("Suspicious operation detected. {detail}")
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
        """Initializes a suspicious operation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class SuspiciousFileOperation(HttpErrorDefinition):
    """Error definition for suspicious file operations.

    This error occurs when a request attempts to perform a file operation
    that appears suspicious, such as path traversal attempts.

    Attributes:
        code: "HTTP:SUSPICIOUS_FILE_OPERATION"
        http_status: 400 Bad Request
        message_template: "Suspicious file operation: {detail}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(SuspiciousFileOperation(
        ...     detail="Path traversal attempt detected"
        ... ))
    """

    code = "HTTP:SUSPICIOUS_FILE_OPERATION"
    http_status = 400
    message_template = _n("Suspicious file operation: {detail}")
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
        """Initializes a suspicious file operation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class SuspiciousMultipartForm(HttpErrorDefinition):
    """Error definition for suspicious multipart form data.

    This error occurs when a request contains multipart form data that
    appears suspicious or malformed.

    Attributes:
        code: "HTTP:SUSPICIOUS_MULTIPART_FORM"
        http_status: 400 Bad Request
        message_template: "Suspicious multipart form data: {detail}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(SuspiciousMultipartForm(
        ...     detail="Missing boundary parameter"
        ... ))
    """

    code = "HTTP:SUSPICIOUS_MULTIPART_FORM"
    http_status = 400
    message_template = _n("Suspicious multipart form data: {detail}")
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
        """Initializes a suspicious multipart form error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class SuspiciousRemoteAddr(HttpErrorDefinition):
    """Error definition for suspicious remote addresses.

    This error occurs when a request originates from a remote address
    that appears suspicious, spoofed, or blocked.

    Attributes:
        code: "HTTP:SUSPICIOUS_REMOTE_ADDR"
        http_status: 400 Bad Request
        message_template: "Suspicious remote address: {detail}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(SuspiciousRemoteAddr(
        ...     detail="Request from blocked IP range"
        ... ))
    """

    code = "HTTP:SUSPICIOUS_REMOTE_ADDR"
    http_status = 400
    message_template = _n("Suspicious remote address: {detail}")
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
        """Initializes a suspicious remote address error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class TooManyFieldsSent(HttpErrorDefinition):
    """Error definition for exceeding maximum field count in requests.

    This error occurs when a request sends more fields than the server
    is configured to accept.

    Attributes:
        code: "HTTP:TOO_MANY_FIELDS"
        http_status: 400 Bad Request
        message_template: "Too many form fields sent. Maximum allowed: {max_fields}"
        is_retryable: False (requires reducing fields)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(TooManyFieldsSent(max_fields=1000))
    """

    code = "HTTP:TOO_MANY_FIELDS"
    http_status = 400
    message_template = _n("Too many form fields sent. Maximum allowed: {max_fields}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        max_fields: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a too many fields error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class RequestDataTooBig(HttpErrorDefinition):
    """Error definition for request data exceeding size limits.

    This error occurs when the request body exceeds the maximum allowed
    size configured on the server.

    Attributes:
        code: "HTTP:REQUEST_DATA_TOO_BIG"
        http_status: 413 Payload Too Large
        message_template: "Request data too large. Maximum allowed: {max_size} {unit}"
        is_retryable: False (requires reducing data size)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(RequestDataTooBig(max_size=2*1024*1024, unit="bytes"))
    """

    code = "HTTP:REQUEST_DATA_TOO_BIG"
    http_status = 413
    message_template = _n("Request data too large. Maximum allowed: {max_size} {unit}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        max_size: int | None = None,
        unit: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a request data too big error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Resolver404(HttpErrorDefinition):
    """Error definition for URL resolution failures.

    This error occurs when no URL pattern matches the requested path.

    Attributes:
        code: "HTTP:RESOLVER_404"
        http_status: 404 Not Found
        message_template: "No matching URL pattern found for the request."
        is_retryable: False (requires valid URL)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(Resolver404())
    """

    code = "HTTP:RESOLVER_404"
    http_status = 404
    message_template = _n("No matching URL pattern found for the request.")
    is_retryable = False


class DisallowedHost(HttpErrorDefinition):
    """Error definition for disallowed host headers.

    This error occurs when the request's Host header does not match
    any allowed hosts configured in the application.

    Attributes:
        code: "HTTP:DISALLOWED_HOST"
        http_status: 400 Bad Request
        message_template: "Host '{host}' not allowed."
        is_retryable: False (requires valid host header)

    Example:
        >>> # Wrap this definition in an HTTP-specific exception
        ... raise HttpError(DisallowedHost(host="malicious-site.com"))
    """

    code = "HTTP:DISALLOWED_HOST"
    http_status = 400
    message_template = _n("Host '{host}' not allowed.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        host: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a disallowed host error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
