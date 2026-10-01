"""Provides base exception classes for different error categories.

This module defines foundational exception classes that serve as category-specific
base classes for various error types including application, authentication,
business logic, database, external services, HTTP, system, and validation
errors. Each exception class wraps a corresponding error definition category
and carries an appropriate severity level.

IMPORTANT - What these classes represent:
    - These are BASE EXCEPTION classes for different error categories
    - Each exception wraps an ErrorDefinition category (blueprint)
    - They define WHEN and WHY errors in each category happen
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the error looks like" (blueprint)
    - Exception classes (here) = "WHEN the error happens" (raised in code flow)
"""

from core.exceptions.base import BaseAppException, ExceptionSeverity
from core.exceptions.errors.common import (
    AppErrorDefinition,
    AuthErrorDefinition,
    BizErrorDefinition,
    DbErrorDefinition,
    ExtErrorDefinition,
    HttpErrorDefinition,
    SysErrorDefinition,
    ValidErrorDefinition,
)


class AppError(BaseAppException[AppErrorDefinition]):
    """Base exception for generic application errors.

    Extended by concrete exceptions that don't fit into more specific
    categories. Serves as a catch-all for unclassified errors.

    Severity: ERROR - These indicate unexpected application issues
    that need investigation but don't require immediate service stop.

    Common scenarios:
    - Unexpected system state
    - Unhandled edge cases
    - Fallback for unknown error types

    Attributes:
        _error_cls: The AppErrorDefinition error definition class.
        severity: ERROR - unexpected application issues.
    """

    _error_cls = AppErrorDefinition
    severity = ExceptionSeverity.ERROR


class AuthError(BaseAppException[AuthErrorDefinition]):
    """Base exception for authentication and authorization errors.

    Extended by concrete exceptions related to:
    - Token validation (invalid, expired)
    - Permission checks (insufficient permissions)
    - Account status (locked, inactive)
    - Credential validation

    Severity: INFO - Authentication failures are expected operational
    occurrences that don't indicate system problems.

    Common scenarios:
    - Invalid login credentials
    - Expired or invalid tokens
    - Insufficient permissions for action
    - Locked or inactive accounts

    Attributes:
        _error_cls: The AuthErrorDefinition error definition class.
        severity: INFO - expected operational occurrences.
    """

    _error_cls = AuthErrorDefinition
    severity = ExceptionSeverity.INFO


class BusinessError(BaseAppException[BizErrorDefinition]):
    """Base exception for business logic violations.

    Extended by concrete exceptions related to:
    - Resource conflicts (duplicate, locked)
    - State violations (operation not allowed)
    - Quota and rate limit exceedances
    - Domain rule violations

    Severity: INFO/WARNING - Business rule violations are normal
    application behavior, though some may indicate misuse patterns.

    Common scenarios:
    - Duplicate resource creation
    - Operation not allowed in current state
    - Quota limits exceeded
    - Resource not found

    Attributes:
        _error_cls: The BizErrorDefinition error definition class.
        severity: INFO - normal business rule violations.
    """

    _error_cls = BizErrorDefinition
    severity = ExceptionSeverity.INFO


class DatabaseError(BaseAppException[DbErrorDefinition]):
    """Base exception for database operation errors.

    Extended by concrete exceptions related to:
    - Connection failures
    - Integrity constraint violations
    - Deadlocks and conflicts
    - Query execution failures

    Severity: ERROR - Database issues typically indicate infrastructure
    problems or data consistency issues requiring attention.

    Common scenarios:
    - Database connection loss
    - Unique constraint violations
    - Deadlock detection
    - Query syntax errors

    Attributes:
        _error_cls: The DbErrorDefinition error definition class.
        severity: ERROR - infrastructure or data consistency issues.
    """

    _error_cls = DbErrorDefinition
    severity = ExceptionSeverity.ERROR


class ExternalError(BaseAppException[ExtErrorDefinition]):
    """Base exception for external service errors.

    Extended by concrete exceptions related to:
    - External API call failures
    - Payment gateway errors
    - Email sending failures
    - Timeout and connectivity issues

    Severity: ERROR - External service failures affect application
    functionality and need monitoring, though may be transient.

    Common scenarios:
    - Third-party API unavailable
    - Payment processing failure
    - Email delivery failure
    - External service timeout

    Attributes:
        _error_cls: The ExtErrorDefinition error definition class.
        severity: ERROR - external service failures.
    """

    _error_cls = ExtErrorDefinition
    severity = ExceptionSeverity.ERROR


class HttpError(BaseAppException[HttpErrorDefinition]):
    """Base exception for HTTP protocol errors.

    Extended by concrete exceptions related to:
    - Bad requests (400)
    - Not found (404)
    - Unauthorized (401)
    - Forbidden (403)
    - Method not allowed (405)
    - Rate limiting (429)

    Severity: INFO - HTTP errors are normal client-server communication
    issues that don't indicate system problems.

    Common scenarios:
    - Missing required parameters
    - Resource not found
    - Authentication required
    - Rate limit exceeded

    Attributes:
        _error_cls: The HttpErrorDefinition error definition class.
        severity: INFO - normal client-server communication issues.
    """

    _error_cls = HttpErrorDefinition
    severity = ExceptionSeverity.INFO


class SystemError(BaseAppException[SysErrorDefinition]):
    """Base exception for system-level errors.

    Extended by concrete exceptions related to:
    - Internal server errors
    - Service unavailability
    - Timeout conditions
    - Configuration issues

    Severity: ERROR/CRITICAL - System errors indicate infrastructure
    or configuration problems requiring immediate attention.

    Common scenarios:
    - Unhandled exceptions
    - Service overload or maintenance
    - Request timeout
    - Misconfiguration or missing settings

    Attributes:
        _error_cls: The SysErrorDefinition error definition class.
        severity: ERROR - infrastructure or configuration problems.
    """

    _error_cls = SysErrorDefinition
    severity = ExceptionSeverity.ERROR


class ValidationError(BaseAppException[ValidErrorDefinition]):
    """Base exception for data validation errors.

    Extended by concrete exceptions related to:
    - Required field validation
    - Format validation (email, phone)
    - Length validation (too long, too short)
    - Range and pattern validation

    Severity: INFO - Validation failures are expected user input
    issues that don't indicate system problems.

    Common scenarios:
    - Missing required field
    - Invalid email or phone format
    - Field value exceeds length limit
    - Value outside allowed range

    Attributes:
        _error_cls: The ValidErrorDefinition error definition class.
        severity: INFO - expected user input issues.
    """

    _error_cls = ValidErrorDefinition
    severity = ExceptionSeverity.INFO
