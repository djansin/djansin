"""Provides Django exception wrappers that integrate with the error definition framework.

This module defines error classes that wrap Django's built-in exceptions,
converting them to the standardized error format used throughout the application.
Each Django exception is mapped to an appropriate error category with proper
HTTP status codes and message templates.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a Django error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exception handlers use these definitions for consistent API responses

Key distinction:
    - ErrorDefinition classes = "WHAT the Django error looks like" (blueprint)
    - Django exceptions = raised by Django framework, converted via custom handler

Relationship with other components:
    - Used by Django exception handlers for consistent error responses
    - Categories include Auth, Business, System, and Validation errors
    - Each maps to appropriate base error definition category
"""

from sqlite3 import IntegrityError, OperationalError
from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors import (
    AuthErrorDefinition,
    BizErrorDefinition,
    SysErrorDefinition,
    ValidErrorDefinition,
)
from core.exceptions.errors.auth import PermissionDenied
from core.exceptions.errors.database import Database, ProtectedError
from core.exceptions.errors.http import (
    BadRequest,
    DisallowedHost,
    NotFound,
    RequestDataTooBig,
    Resolver404,
    SuspiciousFileOperation,
    SuspiciousMultipartForm,
    SuspiciousOperation,
    SuspiciousRemoteAddr,
    TooManyFieldsSent,
)
from core.exceptions.errors.validation import UploadedFileError, Validation


class DisallowedModelAdmin(AuthErrorDefinition):
    """Error definition for disallowed model admin access.

    Used when a user attempts to access a model admin action without permission.

    Attributes:
        code: AUTH_DISALLOWED_MODEL_ADMIN
        http_status: 403 Forbidden
        message_template: Access to model admin is not allowed.
        is_retryable: False
    """

    code = "AUTH_DISALLOWED_MODEL_ADMIN"
    http_status = 403
    message_template = _n("Access to model admin is not allowed.")
    is_retryable = False


class BadSignature(AuthErrorDefinition):
    """Error definition for invalid cryptographic signature.

    Used when a cryptographic signature is invalid or has been tampered with.

    Attributes:
        code: AUTH_BAD_SIGNATURE
        http_status: 401 Unauthorized
        message_template: Invalid or tampered signature.
        is_retryable: False
    """

    code = "AUTH_BAD_SIGNATURE"
    http_status = 401
    message_template = _n("Invalid or tampered signature.")
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
        """Initializes a bad signature error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class SignatureExpired(AuthErrorDefinition):
    """Error definition for expired cryptographic signature.

    Used when a signed value has passed its expiration timestamp.

    Attributes:
        code: AUTH_SIGNATURE_EXPIRED
        http_status: 401 Unauthorized
        message_template: Signature has expired.
        is_retryable: False
    """

    code = "AUTH_SIGNATURE_EXPIRED"
    http_status = 401
    message_template = _n("Signature has expired.")
    is_retryable = False


class ObjectDoesNotExist(BizErrorDefinition):
    """Error definition for missing database object.

    Used when a database query using .get() returns no results.

    Attributes:
        code: BIZ_OBJECT_DOES_NOT_EXIST
        http_status: 404 Not Found
        message_template: {model_name} matching query does not exist.
        is_retryable: False
    """

    code = "BIZ_OBJECT_DOES_NOT_EXIST"
    http_status = 404
    message_template = _n("{model_name} matching query does not exist.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an object does not exist error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class MultipleObjectsReturned(BizErrorDefinition):
    """Error definition for ambiguous database query results.

    Used when a database query using .get() returns more than one result.

    Attributes:
        code: BIZ_MULTIPLE_OBJECTS_RETURNED
        http_status: 409 Conflict
        message_template: Multiple {model_name} objects returned when expected one.
        is_retryable: False
    """

    code = "BIZ_MULTIPLE_OBJECTS_RETURNED"
    http_status = 409
    message_template = _n("Multiple {model_name} objects returned when expected one.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a multiple objects returned error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class AppRegistryNotReady(SysErrorDefinition):
    """Error definition for app registry access too early.

    Used when the Django app registry is accessed before it has been fully loaded.

    Attributes:
        code: SYS_APP_REGISTRY_NOT_READY
        http_status: 500 Internal Server Error
        message_template: App registry not ready. Access too early in startup.
        is_retryable: False
    """

    code = "SYS_APP_REGISTRY_NOT_READY"
    http_status = 500
    message_template = _n("App registry not ready. Access too early in startup.")
    is_retryable = False


class InvalidCacheBackendError(SysErrorDefinition):
    """Error definition for invalid cache backend configuration.

    Used when an invalid cache backend is configured or fails to initialize.

    Attributes:
        code: SYS_INVALID_CACHE_BACKEND
        http_status: 500 Internal Server Error
        message_template: Invalid cache backend: {backend_name}
        is_retryable: False
    """

    code = "SYS_INVALID_CACHE_BACKEND"
    http_status = 500
    message_template = _n("Invalid cache backend: {backend_name}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        backend_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid cache backend error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class NoReverseMatch(SysErrorDefinition):
    """Error definition for URL reverse lookup failure.

    Used when a URL reverse lookup fails (e.g., using the `url` template tag with invalid arguments).

    Attributes:
        code: SYS_NO_REVERSE_MATCH
        http_status: 500 Internal Server Error
        message_template: URL reverse match failed for view '{view_name}'
        is_retryable: False
    """

    code = "SYS_NO_REVERSE_MATCH"
    http_status = 500
    message_template = _n("URL reverse match failed for view '{view_name}'")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        view_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a no reverse match error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ImproperlyConfigured(SysErrorDefinition):
    """Error definition for Django configuration errors.

    Used when Django is misconfigured (missing required settings or invalid values).

    Attributes:
        code: SYS_IMPROPERLY_CONFIGURED
        http_status: 500 Internal Server Error
        message_template: Django configuration error: {detail}
        is_retryable: False
    """

    code = "SYS_IMPROPERLY_CONFIGURED"
    http_status = 500
    message_template = _n("Django configuration error: {detail}")
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
        """Initializes an improperly configured error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class MiddlewareNotUsed(SysErrorDefinition):
    """Error definition for middleware exclusion.

    Used in middleware's __init__ method to indicate that the middleware should not be used.

    Attributes:
        code: SYS_MIDDLEWARE_NOT_USED
        http_status: 500 Internal Server Error
        message_template: Middleware not used: {middleware_name}
        is_retryable: False
    """

    code = "SYS_MIDDLEWARE_NOT_USED"
    http_status = 500
    message_template = _n("Middleware not used: {middleware_name}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        middleware_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a middleware not used error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class FieldError(ValidErrorDefinition):
    """Error definition for model field access errors.

    Used when a model field is accessed incorrectly (invalid lookup, non-existent field).

    Attributes:
        code: VALID_FIELD_ERROR
        http_status: 400 Bad Request
        message_template: Field error: {detail}
        is_retryable: False
    """

    code = "VALID_FIELD_ERROR"
    http_status = 400
    message_template = _n("Field error: {detail}")
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
        """Initializes a field error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class UnicodeDecodeError(ValidErrorDefinition):
    """Error definition for character encoding issues.

    Used when decoding bytes to string fails during request processing or file handling.

    Attributes:
        code: VALID_UNICODE_DECODE_ERROR
        http_status: 400 Bad Request
        message_template: Invalid character encoding. {detail}
        is_retryable: False
    """

    code = "VALID_UNICODE_DECODE_ERROR"
    http_status = 400
    message_template = _n("Invalid character encoding. {detail}")
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
        """Initializes a unicode decode error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


# ===== Error Codes Registry =====
class ErrorCodes:
    """Central registry of Django exception error class references.

    This class provides a convenient namespace for accessing Django exception
    error classes throughout the application, ensuring consistent error handling
    and reducing import duplication.

    Categories:
        - HTTP & View Exceptions: 404, PermissionDenied, BadRequest
        - Suspicious Operations: SuspiciousOperation variants
        - Request & Data: TooManyFields, RequestDataTooBig
        - Database Exceptions: Database, IntegrityError, etc.
        - ORM & Model Exceptions: ObjectDoesNotExist, MultipleObjectsReturned
        - Validation: Validation
        - URL & Routing: Resolver404, NoReverseMatch
        - Configuration: ImproperlyConfigured, MiddlewareNotUsed
        - Signing: BadSignature, SignatureExpired
        - File Upload: UploadedFileError
        - Host & Admin: DisallowedHost, DisallowedModelAdmin
    """

    # ===== HTTP & View Exceptions =====
    DJANGO_404_NOT_FOUND = NotFound
    DJANGO_PERMISSION_DENIED = PermissionDenied
    DJANGO_BAD_REQUEST = BadRequest

    # ===== Suspicious Operations =====
    DJANGO_SUSPICIOUS_OPERATION = SuspiciousOperation
    DJANGO_SUSPICIOUS_FILE_OPERATION = SuspiciousFileOperation
    DJANGO_SUSPICIOUS_MULTIPART_FORM = SuspiciousMultipartForm
    DJANGO_SUSPICIOUS_REMOTE_ADDR = SuspiciousRemoteAddr

    # ===== Request & Data =====
    DJANGO_TOO_MANY_FIELDS = TooManyFieldsSent
    DJANGO_REQUEST_DATA_TOO_BIG = RequestDataTooBig

    # ===== Database Exceptions =====
    DJANGO_DATABASE_ERROR = Database
    DJANGO_INTEGRITY_ERROR = IntegrityError
    DJANGO_OPERATIONAL_ERROR = OperationalError
    DJANGO_PROTECTED_ERROR = ProtectedError

    # ===== ORM & Model Exceptions =====
    DJANGO_OBJECT_DOES_NOT_EXIST = ObjectDoesNotExist
    DJANGO_MULTIPLE_OBJECTS_RETURNED = MultipleObjectsReturned
    DJANGO_FIELD_ERROR = FieldError

    # ===== Validation =====
    DJANGO_VALIDATION_ERROR = Validation

    # ===== URL & Routing =====
    DJANGO_RESOLVER_404 = Resolver404
    DJANGO_NO_REVERSE_MATCH = NoReverseMatch

    # ===== Configuration =====
    DJANGO_IMPROPERLY_CONFIGURED = ImproperlyConfigured
    DJANGO_MIDDLEWARE_NOT_USED = MiddlewareNotUsed
    DJANGO_APP_REGISTRY_NOT_READY = AppRegistryNotReady

    # ===== Encoding =====
    DJANGO_UNICODE_DECODE_ERROR = UnicodeDecodeError

    # ===== Cache =====
    DJANGO_INVALID_CACHE_BACKEND = InvalidCacheBackendError

    # ===== Signing =====
    DJANGO_BAD_SIGNATURE = BadSignature
    DJANGO_SIGNATURE_EXPIRED = SignatureExpired

    # ===== File Upload =====
    DJANGO_UPLOAD_ERROR = UploadedFileError

    # ===== Host & Admin =====
    DJANGO_DISALLOWED_HOST = DisallowedHost
    DJANGO_DISALLOWED_MODEL_ADMIN = DisallowedModelAdmin
