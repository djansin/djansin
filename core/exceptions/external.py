"""Provides external service exception classes for third-party integrations.

This module defines concrete exception classes that wrap external service
error definitions. Each exception corresponds to a specific external service
error scenario and carries an appropriate severity level for monitoring and
alerting purposes.

IMPORTANT - What these classes represent:
    - These are EXCEPTION classes (raised at runtime)
    - Each exception wraps an ErrorDefinition (blueprint)
    - They define WHEN and WHY an external service error happens
    - The severity determines monitoring and alerting responses

Key distinction:
    - ErrorDefinition classes = "WHAT the external error looks like" (blueprint)
    - Exception classes (here) = "WHEN the external error happens" (raised in code flow)
"""

from typing import overload

from core.exceptions.base import ExceptionSeverity
from core.exceptions.common import ExternalError
from core.exceptions.errors.common import ExtErrorDefinition
from core.exceptions.errors.external import ExtApi, ExtEmail, ExtPayment, Timeout


class ExternalApiError(ExternalError):
    """Raised when an external API call fails.

    This exception is raised when external API calls fail due to HTTP errors,
    network issues, malformed responses, or service-specific errors.

    Common scenarios:
    - External service returns 4xx or 5xx HTTP status
    - Network connectivity issues to external service
    - Malformed JSON or unexpected response format
    - Authentication failure with external service
    - Rate limiting from external service

    This error IS retryable as external services may recover.

    Attributes:
        _error_cls: The ExtApi error definition class.
        severity: ERROR - external API failures affect application functionality.
    """

    _error_cls = ExtApi
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | ExtErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ExtErrorDefinition | None = None, /, **kwds):
        """Initializes an external API error exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class ExternalTimeoutError(ExternalError):
    """Raised when an external service times out.

    This exception is raised when an external service does not respond within
    the expected timeframe, whether at network level or application level.

    Common scenarios:
    - External API takes too long to respond
    - Database query on external service times out
    - Network-level timeout (connect, read, write)
    - Load balancer or proxy timeout
    - External service under heavy load

    This error IS retryable as timeouts may be transient.

    Attributes:
        _error_cls: The Timeout error definition class.
        severity: ERROR - timeouts indicate performance issues.
    """

    _error_cls = Timeout
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | ExtErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ExtErrorDefinition | None = None, /, **kwds):
        """Initializes an external timeout error exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)


class PaymentError(ExternalError):
    """Raised when a payment processing operation fails.

    This exception is raised when a payment gateway rejects a transaction,
    processing fails, or payment-related external service errors occur.

    Common scenarios:
    - Insufficient funds on payment method
    - Expired credit card
    - Payment gateway rejects transaction
    - Fraud detection system blocks payment
    - Invalid payment method details
    - Payment service temporarily unavailable

    This error is NOT retryable as it typically requires user intervention
    or payment method update.

    Attributes:
        _error_cls: The ExtPayment error definition class.
        severity: ERROR - payment failures affect business transactions.
    """

    _error_cls = ExtPayment
    severity = ExceptionSeverity.ERROR


class EmailError(ExternalError):
    """Raised when an email sending operation fails.

    This exception is raised when email service fails to send messages due
    to SMTP errors, rate limiting, temporary service issues, or invalid
    recipient addresses.

    Common scenarios:
    - SMTP server connection failure
    - Invalid recipient email address
    - Rate limiting from email service provider
    - Email quota exceeded
    - Attachment size too large
    - Email service authentication failure

    This error IS retryable as email delivery issues may be transient.

    Attributes:
        _error_cls: The ExtEmail error definition class.
        severity: ERROR - email failures affect notifications.
    """

    _error_cls = ExtEmail
    severity = ExceptionSeverity.ERROR

    @overload
    def __init__(
        self,
        error: str | ExtErrorDefinition | None = None,
        /,
        *,
        reference_id: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, error: str | ExtErrorDefinition | None = None, /, **kwds):
        """Initializes an email error exception.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(error, **kwds)
