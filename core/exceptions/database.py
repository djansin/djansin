"""Provides database exception classes for common data access failures.

This module defines concrete exception classes that wrap database error
definitions. Each exception corresponds to a specific database error scenario
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY a database error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the database error looks like" (blueprint)
    - Exception classes (here) = "WHEN the database error happens" (raised in code flow)
"""

from typing import overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import DatabaseError
from core.exceptions.errors.common import DbErrorDefinition
from core.exceptions.errors.database import (
    DbConflict,
    DbConnection,
    DbDeadlock,
    DbIntegrity,
    DbQuery,
)


class DbConnectionError(DatabaseError):
    """Raised when a database connection fails.

    This exception is raised when the application cannot establish or maintain
    a connection to the database.

    Common scenarios:
    - Database server is down or unreachable
    - Network connectivity issues between app and database
    - Connection pool exhausted
    - Database authentication failure
    - Database server overloaded

    This error IS retryable as connection problems may be transient.

    Attributes:
        _error_cls: The DbConnection error definition class.
        severity: ERROR - database connectivity issues require monitoring.
    """

    _error_cls = DbConnection
    severity = ExceptionSeverity.ERROR


class DbIntegrityError(DatabaseError):
    """Raised when a database integrity constraint is violated.

    This exception is raised when an operation would violate a database
    constraint such as foreign key, unique, or check constraints.

    Common scenarios:
    - Duplicate key violation (unique constraint)
    - Foreign key reference to non-existent record
    - Check constraint violation (e.g., negative price, invalid status)
    - NOT NULL constraint violation
    - Exclusion constraint violation (PostgreSQL)

    This error is NOT retryable as it requires data changes to resolve.

    Attributes:
        _error_cls: The DbIntegrity error definition class.
        severity: ERROR - data consistency issues need investigation.
    """

    _error_cls = DbIntegrity
    severity = ExceptionSeverity.ERROR


class DbDeadlockError(DatabaseError):
    """Raised when a database deadlock is detected.

    This exception is raised when a database deadlock occurs due to circular
    lock dependencies between transactions.

    Common scenarios:
    - Two transactions trying to update the same records in different orders
    - Long-running transactions causing lock contention
    - High concurrency with pessimistic locking
    - Mixed lock acquisition order in different code paths

    This error IS retryable as deadlocks often resolve on retry.

    Attributes:
        _error_cls: The DbDeadlock error definition class.
        severity: ERROR - deadlocks indicate concurrency issues to monitor.
    """

    _error_cls = DbDeadlock
    severity = ExceptionSeverity.ERROR


class DbQueryError(DatabaseError):
    """Raised when a database query execution fails.

    This exception is raised when a database query fails due to syntax errors,
    invalid parameters, or other query-related issues.

    Common scenarios:
    - SQL syntax error
    - Invalid parameter types or values
    - Query timeout exceeded
    - Permission denied for operation
    - Too many connections or resources exhausted

    This error is NOT retryable as it typically requires code or data fixes.

    Attributes:
        _error_cls: The DbQuery error definition class.
        severity: ERROR - query failures need code investigation.
    """

    _error_cls = DbQuery
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | DbErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | DbErrorDefinition | None = None, /, **kwds):
        """Initializes a database query exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class DbConflictError(DatabaseError):
    """Raised when a database concurrent modification conflict occurs.

    This exception is raised for optimistic locking or concurrent modification
    failures where a record was changed by another transaction.

    Common scenarios:
    - Optimistic locking version mismatch
    - Record was modified by another user between read and write
    - Concurrent update detected in high-traffic areas
    - Stale data being updated after another transaction committed
    - Row-level lock acquisition timeout

    This error is NOT retryable as it requires data refresh and user action.

    Attributes:
        _error_cls: The DbConflict error definition class.
        severity: ERROR - conflicts indicate concurrency coordination needs review.
    """

    _error_cls = DbConflict
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | DbErrorDefinition | None = None,
        /,
        *,
        details: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | DbErrorDefinition | None = None, /, **kwds):
        """Initializes a database conflict exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
