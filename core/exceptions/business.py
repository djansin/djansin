"""Provides business logic exception classes for common domain rule violations.

This module defines concrete exception classes that wrap business logic error
definitions. Each exception corresponds to a specific business rule violation
and carries an appropriate severity level for monitoring and alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY a business error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the business error looks like" (blueprint)
    - Exception classes (here) = "WHEN the business error happens" (raised in code flow)
"""

from typing import overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import BusinessError
from core.exceptions.errors.business import (
    DuplicateResource,
    InsufficientFunds,
    OperationNotAllowed,
    QuotaExceeded,
    RateLimited,
    ResourceLocked,
    ResourceNotFound,
)
from core.exceptions.errors.common import BizErrorDefinition


class InsufficientFundsError(BusinessError):
    """Raised when a financial operation cannot be completed due to insufficient funds.

    This exception is raised when an account doesn't have enough balance to
    complete a transaction (withdrawal, payment, transfer). Carries INFO
    severity as this is a normal business rule violation, not a system error.

    Common scenarios:
    - User tries to withdraw more than account balance
    - Payment amount exceeds available credit
    - Transfer amount greater than available funds
    - Insufficient balance for subscription renewal

    This error is NOT retryable as retrying won't create more funds.

    Attributes:
        _error_cls: The InsufficientFunds error definition class.
        severity: INFO - normal business rule violation.
    """

    _error_cls = InsufficientFunds
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        required: float | None = None,
        available: float | None = None,
        currency: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes an insufficient funds exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class DuplicateResourceError(BusinessError):
    """Raised when attempting to create a resource that already exists.

    This exception is raised when an operation tries to create a resource
    with an identifier that is already in use. Carries INFO severity as this
    is a common business rule violation.

    Common scenarios:
    - User registration with existing email/username
    - Creating a product with duplicate SKU
    - Adding a duplicate entry to a unique collection
    - Creating a record with existing foreign key constraint

    This error is NOT retryable as the duplicate condition persists.

    Attributes:
        _error_cls: The DuplicateResource error definition class.
        severity: INFO - common business rule violation.
    """

    _error_cls = DuplicateResource
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        resource: str | None = None,
        field_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes a duplicate resource exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class ResourceLockedError(BusinessError):
    """Raised when attempting to modify a locked resource.

    This exception is raised when an operation tries to modify a resource
    that is currently locked (e.g., due to an ongoing process, pessimistic
    locking, or administrative action). Carries INFO severity.

    Common scenarios:
    - Document being edited by another user
    - Resource under workflow review
    - Administrative lock placed on account
    - Resource locked by batch process

    This error is NOT retryable as the lock must be released first.

    Attributes:
        _error_cls: The ResourceLocked error definition class.
        severity: INFO - normal operational occurrence.
    """

    _error_cls = ResourceLocked
    severity = ExceptionSeverity.INFO


class QuotaExceededError(BusinessError):
    """Raised when a usage quota has been exceeded.

    This exception is raised when a user or system exceeds an allocated quota
    such as API call limits, storage limits, or usage caps. Carries WARNING
    severity as this may indicate abusive behavior or capacity planning issues.

    Common scenarios:
    - Daily API request limit exceeded
    - Storage quota exceeded
    - Monthly transaction limit reached
    - Concurrent connection limit exceeded

    This error is NOT retryable as quota limits typically require time or upgrade.

    Attributes:
        _error_cls: The QuotaExceeded error definition class.
        severity: WARNING - may indicate capacity or abuse issues.
    """

    _error_cls = QuotaExceeded
    severity = ExceptionSeverity.WARNING

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        resource: str | None = None,
        limit: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes a quota exceeded exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class OperationNotAllowedError(BusinessError):
    """Raised when an operation is not allowed in the current state.

    This exception is raised when an operation is attempted but the current
    state of the system or resource does not permit it. Carries WARNING
    severity as this may indicate invalid state transitions.

    Common scenarios:
    - Cancelling an already completed order
    - Editing a published post
    - Deleting a non-empty category
    - Transition to invalid workflow state

    This error is NOT retryable as the state must change first.

    Attributes:
        _error_cls: The OperationNotAllowed error definition class.
        severity: WARNING - may indicate invalid state transitions.
    """

    _error_cls = OperationNotAllowed
    severity = ExceptionSeverity.WARNING

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        reason: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes an operation not allowed exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class ResourceNotFoundError(BusinessError):
    """Raised when a requested resource cannot be found.

    This exception is raised when an operation tries to access a resource
    that does not exist in the system. Carries INFO severity as this is a
    common occurrence in normal operation.

    Common scenarios:
    - User profile not found by ID
    - Product not found by SKU
    - Order not found by reference number
    - API endpoint with non-existent resource ID

    This error is NOT retryable as the resource doesn't exist.

    Attributes:
        _error_cls: The ResourceNotFound error definition class.
        severity: INFO - common operational occurrence.
    """

    _error_cls = ResourceNotFound
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        resource: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes a resource not found exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class RateLimitedError(BusinessError):
    """Raised when a rate limit has been exceeded.

    This exception is raised when a client has made too many requests within
    a given time window. Carries INFO severity as this is a normal rate
    limiting mechanism.

    Common scenarios:
    - API rate limit exceeded
    - Login attempt rate limiting
    - Email sending rate limiting
    - Search request throttling

    This error IS retryable after waiting the specified period.

    Attributes:
        _error_cls: The RateLimited error definition class.
        severity: INFO - normal rate limiting mechanism.
    """

    _error_cls = RateLimited
    severity = ExceptionSeverity.INFO

    @overload
    def __init__(
        self,
        error: str | BizErrorDefinition | None = None,
        /,
        *,
        retry_after: int | None = None,
        unit: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | BizErrorDefinition | None = None, /, **kwds):
        """Initializes a rate limited exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
