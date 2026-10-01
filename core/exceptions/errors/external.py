"""Provides external service error definitions for third-party integrations.

This module defines concrete error definition classes for external service
errors including API failures, timeouts, payment processing errors, and
email delivery failures.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW an external service error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like ExternalError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the external error looks like" (blueprint)
    - Exception classes = "WHEN the external error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import ExtErrorDefinition


class ExtApi(ExtErrorDefinition):
    """Error definition for external API service failures.

    This error occurs when an external API call fails due to issues
    such as server errors, malformed responses, or authentication
    problems with the external service.

    Attributes:
        code: "EXT:API_ERROR"
        http_status: 502 Bad Gateway
        message_template: "External service error. Reference: {reference_id}"
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in an external service exception
        ... raise ExternalError(ExtApi(reference_id="API-12345"))
    """

    code = "EXT:API_ERROR"
    http_status = 502
    message_template = _n("External service error. Reference: {reference_id}")
    is_retryable = True

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
        """Initializes an external API error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Timeout(ExtErrorDefinition):
    """Error definition for external service timeouts.

    This error occurs when an external service fails to respond within
    the configured timeout period. The operation may succeed if retried
    as the service might be temporarily slow.

    Attributes:
        code: "EXT:TIMEOUT"
        http_status: 504 Gateway Timeout
        message_template: "External service timeout. Reference: {reference_id}"
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in an external service exception
        ... raise ExternalError(Timeout(reference_id="TO-12345"))
    """

    code = "EXT:TIMEOUT"
    http_status = 504
    message_template = _n("External service timeout. Reference: {reference_id}")
    is_retryable = True

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
        """Initializes an external service timeout error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ExtPayment(ExtErrorDefinition):
    """Error definition for payment processing failures.

    This error occurs when a payment transaction fails to process
    through external payment gateways due to declined payments,
    insufficient funds, or gateway-specific rejections.

    Attributes:
        code: "EXT:PAYMENT_ERROR"
        http_status: 502 Bad Gateway
        message_template: "Payment processing failed. Please try another payment method."
        is_retryable: False (requires different payment method)

    Example:
        >>> # Wrap this definition in a payment service exception
        ... raise ExternalError(ExtPayment())
    """

    code = "EXT:PAYMENT_ERROR"
    http_status = 502
    message_template = _n(
        "Payment processing failed. Please try another payment method."
    )
    is_retryable = False


class ExtEmail(ExtErrorDefinition):
    """Error definition for email delivery failures.

    This error occurs when the application fails to send an email
    through external email service providers due to SMTP errors,
    invalid recipients, or service unavailability.

    Attributes:
        code: "EXT:EMAIL_ERROR"
        http_status: 502 Bad Gateway
        message_template: "Failed to send email. Reference: {reference_id}"
        is_retryable: True (retrying may succeed)

    Example:
        >>> # Wrap this definition in an email service exception
        ... raise ExternalError(ExtEmail(reference_id="EM-12345"))
    """

    code = "EXT:EMAIL_ERROR"
    http_status = 502
    message_template = _n("Failed to send email. Reference: {reference_id}")
    is_retryable = True

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
        """Initializes an email error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
