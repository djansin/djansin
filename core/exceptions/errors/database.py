"""Provides database operation error definitions for common data access failures.

This module defines concrete error definition classes for database-related
errors including connection failures, integrity violations, deadlocks, query
failures, conflicts, operational errors, and protected object deletion issues.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a database error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like DatabaseError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the database error looks like" (blueprint)
    - Exception classes = "WHEN the database error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import DbErrorDefinition


class DbConnection(DbErrorDefinition):
    """Error definition for database connection failures.

    This error occurs when the application cannot establish a connection
    to the database server due to network issues, server unavailability,
    or configuration problems.

    Attributes:
        code: "DB:CONNECTION_ERROR"
        http_status: 503 Service Unavailable
        message_template: "Database connection failed. Please try again later."
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DbConnection())
    """

    code = "DB:CONNECTION_ERROR"
    http_status = 503
    message_template = _n("Database connection failed. Please try again later.")
    is_retryable = True


class DbIntegrity(DbErrorDefinition):
    """Error definition for database integrity constraint violations.

    This error occurs when an operation violates database integrity
    constraints such as foreign key constraints, unique constraints,
    or check constraints.

    Attributes:
        code: "DB:INTEGRITY_ERROR"
        http_status: 409 Conflict
        message_template: "Data integrity violation."
        is_retryable: False (requires data correction)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DbIntegrity())
    """

    code = "DB:INTEGRITY_ERROR"
    http_status = 409
    message_template = _n("Data integrity violation.")
    is_retryable = False


class DbDeadlock(DbErrorDefinition):
    """Error definition for database deadlock detection.

    This error occurs when the database detects a deadlock situation
    where multiple transactions are waiting for each other to release
    locks. The operation can be retried.

    Attributes:
        code: "DB:DEADLOCK_ERROR"
        http_status: 500 Internal Server Error
        message_template: "Database deadlock detected. Please retry."
        is_retryable: True (retrying may resolve deadlock)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DbDeadlock())
    """

    code = "DB:DEADLOCK_ERROR"
    http_status = 500
    message_template = _n("Database deadlock detected. Please retry.")
    is_retryable = True


class DbQuery(DbErrorDefinition):
    """Error definition for database query execution failures.

    This error occurs when a database query fails to execute properly
    due to syntax errors, invalid schema references, or query timeouts.

    Attributes:
        code: "DB:QUERY_ERROR"
        http_status: 500 Internal Server Error
        message_template: "Database query failed. Reference: {reference_id}"
        is_retryable: False (requires query correction)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DbQuery(reference_id="Q-12345"))
    """

    code = "DB:QUERY_ERROR"
    http_status = 500
    message_template = _n("Database query failed. Reference: {reference_id}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a database query error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class DbConflict(DbErrorDefinition):
    """Error definition for database conflict situations.

    This error occurs when an operation conflicts with existing data
    or concurrent modifications in the database.

    Attributes:
        code: "DB:CONFLICT_ERROR"
        http_status: 409 Conflict
        message_template: "Database conflict. {details}"
        is_retryable: False (requires manual resolution)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DbConflict(
        ...     details="Record was modified by another user"
        ... ))
    """

    code = "DB:CONFLICT_ERROR"
    http_status = 409
    message_template = _n("Database conflict. {details}")
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
        """Initializes a database conflict error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class DatabaseError(DbErrorDefinition):
    """Error definition for general database errors.

    This error occurs when a general database operation fails without
    falling into more specific error categories.

    Attributes:
        code: "DB:DATABASE_ERROR"
        http_status: 500 Internal Server Error
        message_template: "Database error occurred. Reference: {reference_id}"
        is_retryable: False (requires investigation)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(DatabaseError(reference_id="DB-12345"))
    """

    code = "DB:DATABASE_ERROR"
    http_status = 500
    message_template = _n("Database error occurred. Reference: {reference_id}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a database error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class IntegrityError(DbErrorDefinition):
    """Error definition for detailed integrity constraint violations.

    This error occurs when a database operation violates integrity
    constraints with additional context about the specific violation.

    Attributes:
        code: "DB:INTEGRITY_ERROR"
        http_status: 409 Conflict
        message_template: "Database integrity error: {detail}"
        is_retryable: False (requires data correction)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(IntegrityError(
        ...     detail="Duplicate email address violation on users table"
        ... ))
    """

    code = "DB:INTEGRITY_ERROR"
    http_status = 409
    message_template = _n("Database integrity error: {detail}")
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
        """Initializes an integrity error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class OperationalError(DbErrorDefinition):
    """Error definition for database operational issues.

    This error occurs when there are operational problems with the
    database such as connection timeouts, server unavailability,
    or transaction issues that may be temporary.

    Attributes:
        code: "DB:OPERATIONAL_ERROR"
        http_status: 503 Service Unavailable
        message_template: "Database operational error: {detail}"
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(OperationalError(
        ...     detail="Connection pool exhausted"
        ... ))
    """

    code = "DB:OPERATIONAL_ERROR"
    http_status = 503
    message_template = _n("Database operational error: {detail}")
    is_retryable = True

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
        """Initializes an operational error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ProtectedError(DbErrorDefinition):
    """Error definition for protected object deletion attempts.

    This error occurs when attempting to delete an object that is
    protected by foreign key relationships or other dependencies.

    Attributes:
        code: "DB:PROTECTED_ERROR"
        http_status: 409 Conflict
        message_template: "Cannot delete {model_name}: it is referenced by {protected_objects}"
        is_retryable: False (requires dependency resolution)

    Example:
        >>> # Wrap this definition in a database-specific exception
        ... raise DatabaseError(ProtectedError(
        ...     model_name="Category",
        ...     protected_objects="5 products"
        ... ))
    """

    code = "DB:PROTECTED_ERROR"
    http_status = 409
    message_template = _n(
        "Cannot delete {model_name}: it is referenced by {protected_objects}"
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        protected_objects: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a protected error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
