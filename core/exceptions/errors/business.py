"""Provides business logic error definitions for common domain rule violations.

This module defines concrete error definition classes for business logic-related
errors including insufficient funds, duplicate resources, locked resources,
quota exceedances, operation not allowed, resource not found, rate limiting,
throttling, deletion conflicts, soft-delete state errors, trust level operations,
and verification state errors.

IMPORTANT - What these classes represent:
    - These are ERROR DEFINITIONS (blueprints), NOT exceptions
    - Each definition declares HOW a business error should be represented
    - They define the error code, HTTP status, message template, and retryability
    - Exceptions (like BusinessError) use these definitions for responses

Key distinction:
    - ErrorDefinition classes = "WHAT the business error looks like" (blueprint)
    - Exception classes = "WHEN the business error happens" (raised in code flow)
"""

from typing import overload

from django.utils.translation import gettext_noop as _n

from core.exceptions.errors.common import BizErrorDefinition


class InsufficientFunds(BizErrorDefinition):
    """Error definition for insufficient funds in financial operations.

    This error occurs when a financial transaction cannot be completed due to
    lack of funds. Includes information about required amount, available amount,
    and currency.

    Attributes:
        code: "BIZ:INSUFFICIENT_FUNDS"
        http_status: 422 Unprocessable Entity
        message_template: "Insufficient funds. Required: {required} {currency}, Available: {available} {currency}."
        is_retryable: False (retrying won't create more funds)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(InsufficientFunds(required=100.0, available=50.0))
    """

    code = "BIZ:INSUFFICIENT_FUNDS"
    http_status = 422
    message_template = _n(
        "Insufficient funds. Required: {required} {currency}, Available: {available} {currency}."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        required: float | None = None,
        available: float | None = None,
        currency: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an insufficient funds error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class DuplicateResource(BizErrorDefinition):
    """Error definition for duplicate resource creation attempts.

    This error occurs when attempting to create a resource with an identifier
    that already exists in the system.

    Attributes:
        code: "BIZ:DUPLICATE_RESOURCE"
        http_status: 409 Conflict
        message_template: "{resource} with this {field_name} already exists."
        is_retryable: False (duplicate won't resolve by retrying)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(DuplicateResource(resource="User", field_name="email"))
    """

    code = "BIZ:DUPLICATE_RESOURCE"
    http_status = 409
    message_template = _n("{resource} with this {field_name} already exists.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        resource: str | None = None,
        field_name: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a duplicate resource error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ResourceLocked(BizErrorDefinition):
    """Error definition for locked resource modification attempts.

    This error occurs when attempting to modify a resource that is currently locked.
    Retrying the operation won't resolve the issue as the resource needs to be
    explicitly unlocked first.

    Attributes:
        code: "BIZ:RESOURCE_LOCKED"
        http_status: 423 Locked
        message_template: "Resource is locked and cannot be modified."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceLocked())
    """

    code = "BIZ:RESOURCE_LOCKED"
    http_status = 423
    message_template = _n("Resource is locked and cannot be modified.")
    is_retryable = False


class QuotaExceeded(BizErrorDefinition):
    """Error definition for usage quota violations.

    This error occurs when a user or system exceeds an allocated quota limit.
    Resolution typically requires upgrading the quota or waiting for the quota
    period to reset.

    Attributes:
        code: "BIZ:QUOTA_EXCEEDED"
        http_status: 429 Too Many Requests
        message_template: "{resource} limit exceeded. Maximum allowed: {limit}."
        is_retryable: False (quota exceeded requires time or upgrade)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(QuotaExceeded(resource="API calls", limit=1000))
    """

    code = "BIZ:QUOTA_EXCEEDED"
    http_status = 429
    message_template = _n("{resource} limit exceeded. Maximum allowed: {limit}.")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        resource: str | None = None,
        limit: int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a quota exceeded error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class OperationNotAllowed(BizErrorDefinition):
    """Error definition for invalid state transitions.

    This error occurs when an operation is attempted but the current state of
    the system or resource does not permit it.

    Attributes:
        code: "BIZ:OPERATION_NOT_ALLOWED"
        http_status: 403 Forbidden
        message_template: "Operation not allowed. {reason}"
        is_retryable: False (operation not allowed in this state)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(OperationNotAllowed(reason="Account is inactive"))
    """

    code = "BIZ:OPERATION_NOT_ALLOWED"
    http_status = 403
    message_template = _n("Operation not allowed. {reason}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        reason: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an operation not allowed error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ResourceNotFound(BizErrorDefinition):
    """Error definition for resource lookup failures.

    This error occurs when a requested resource cannot be found in the system.

    Attributes:
        code: "BIZ:RESOURCE_NOT_FOUND"
        http_status: 404 Not Found
        message_template: "{resource} not found."
        is_retryable: False (resource doesn't exist)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceNotFound(resource="Product"))
    """

    code = "BIZ:RESOURCE_NOT_FOUND"
    http_status = 404
    message_template = _n("{resource} not found.")
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
        """Initializes a resource not found error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class RateLimited(BizErrorDefinition):
    """Error definition for rate limit exceedances.

    This error occurs when a client has exceeded the allowed request rate.
    The operation can be retried after the specified waiting period.

    Attributes:
        code: "BIZ:RATE_LIMITED"
        http_status: 429 Too Many Requests
        message_template: "Too many requests. Please try again in {retry_after} {unit}."
        is_retryable: True (can retry after waiting)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(RateLimited(retry_after=30, unit="seconds"))
    """

    code = "BIZ:RATE_LIMITED"
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
        """Initializes a rate limited error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class Throttled(BizErrorDefinition):
    """Error definition for request throttling.

    This error occurs when a request is throttled due to rate limiting policies.
    The operation can be retried after the specified waiting period.

    Attributes:
        code: "BIZ:THROTTLED"
        http_status: 429 Too Many Requests
        message_template: "Request was throttled. Expected available in {wait} seconds."
        is_retryable: True

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(Throttled(wait=60))
    """

    code = "BIZ:THROTTLED"
    http_status = 429
    message_template = _n(
        "Request was throttled. Expected available in {wait} seconds."
    )
    is_retryable = True

    @overload
    def __init__(
        self, message_template: str | None = None, /, *, wait: int | None = None, **kwds
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a throttled error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ObjectNotDeleted(BizErrorDefinition):
    """Error definition for failed deletion attempts.

    This error occurs when attempting to delete an object that has protected
    relationships, is locked, or violates business rules preventing deletion.

    Attributes:
        code: "BIZ:OBJECT_NOT_DELETED"
        http_status: 409 Conflict
        message_template: "Cannot delete {model_name} with ID {object_id}. {reason}"
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ObjectNotDeleted(
        ...     model_name="Order",
        ...     object_id=12345,
        ...     reason="Order has associated payments"
        ... ))
    """

    code = "BIZ:OBJECT_NOT_DELETED"
    http_status = 409
    message_template = _n("Cannot delete {model_name} with ID {object_id}. {reason}")
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        object_id: str | int | None = None,
        reason: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an object not deleted error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class UndeleteActiveObject(BizErrorDefinition):
    """Error definition for attempting to restore a non-deleted object.

    This error occurs when the undelete() method is called on an object
    that is not currently soft-deleted. The operation is only allowed
    on objects that have been previously soft-deleted.

    Attributes:
        code: "BIZ:UNDELETE_ACTIVE_OBJECT"
        http_status: 409 Conflict
        message_template: "Cannot restore {model_name} with ID {object_id}: undelete operation not allowed on active objects."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(UndeleteActiveObject(
        ...     model_name="Post",
        ...     object_id=42
        ... ))
    """

    code = "BIZ:UNDELETE_ACTIVE_OBJECT"
    http_status = 409
    message_template = _n(
        "Cannot restore {model_name} with ID {object_id}: undelete operation not allowed on active objects."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        object_id: str | int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an undelete active object error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ObjectAlreadyDeleted(BizErrorDefinition):
    """Error definition for attempting to delete an already deleted object.

    This error occurs when the delete() method is called on an object
    that is already soft-deleted.

    Attributes:
        code: "BIZ:OBJECT_ALREADY_DELETED"
        http_status: 409 Conflict
        message_template: "Cannot delete {model_name} with ID {object_id}: object is already deleted."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ObjectAlreadyDeleted(
        ...     model_name="Comment",
        ...     object_id=99
        ... ))
    """

    code = "BIZ:OBJECT_ALREADY_DELETED"
    http_status = 409
    message_template = _n(
        "Cannot delete {model_name} with ID {object_id}: object is already deleted."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        model_name: str | None = None,
        object_id: str | int | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an object already deleted error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class ResourceAlreadyBlocked(BizErrorDefinition):
    """Error definition for attempting to block an already blocked resource.

    This error occurs when an operation tries to block a resource that is
    already in a blocked state.

    Attributes:
        code: "BIZ:RESOURCE_ALREADY_BLOCKED"
        http_status: 409 Conflict
        message_template: "The resource is already blocked."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceAlreadyBlocked())
    """

    code = "BIZ:RESOURCE_ALREADY_BLOCKED"
    http_status = 409
    message_template = _n("The resource is already blocked.")
    is_retryable = False


class ResourceAlreadyUnblocked(BizErrorDefinition):
    """Error definition for attempting to unblock an already unblocked resource.

    This error occurs when an operation tries to unblock a resource that is
    already in an unblocked state.

    Attributes:
        code: "BIZ:RESOURCE_ALREADY_UNBLOCKED"
        http_status: 409 Conflict
        message_template: "The resource is already unblocked."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceAlreadyUnblocked())
    """

    code = "BIZ:RESOURCE_ALREADY_UNBLOCKED"
    http_status = 409
    message_template = _n("The resource is already unblocked.")
    is_retryable = False


class ResourceNotSaved(BizErrorDefinition):
    """Error definition for operations on unsaved resources.

    This error occurs when attempting to perform operations like updating,
    deleting, or blocking on a resource instance that hasn't been persisted
    to the database yet.

    Attributes:
        code: "BIZ:RESOURCE_NOT_SAVED"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot perform operation on unsaved resource."
        is_retryable: False

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceNotSaved())
    """

    code = "BIZ:RESOURCE_NOT_SAVED"
    http_status = 422
    message_template = _n("Cannot perform operation on unsaved resource.")
    is_retryable = False


class ResourceAlreadyConfirmed(BizErrorDefinition):
    """Error definition for attempting to confirm an already confirmed resource.

    This error occurs when an operation tries to confirm a resource that is
    already in a confirmed state. Confirmation operations should only be
    performed on unconfirmed resources.

    Attributes:
        code: "BIZ:RESOURCE_ALREADY_CONFIRMED"
        http_status: 409 Conflict
        message_template: "The resource is already confirmed."
        is_retryable: False (resource state cannot be changed)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceAlreadyConfirmed())
    """

    code = "BIZ:RESOURCE_ALREADY_CONFIRMED"
    http_status = 409
    message_template = _n("The resource is already confirmed.")
    is_retryable = False


class ResourceNotConfirmed(BizErrorDefinition):
    """Error definition for operations on unconfirmed resources.

    This error occurs when attempting to perform operations that require
    a confirmed resource but the resource is not yet confirmed.

    Attributes:
        code: "BIZ:RESOURCE_NOT_CONFIRMED"
        http_status: 403 Forbidden
        message_template: "The resource is not confirmed."
        is_retryable: False (requires confirmation)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(ResourceNotConfirmed())
    """

    code = "BIZ:RESOURCE_NOT_CONFIRMED"
    http_status = 403
    message_template = _n("The resource is not confirmed.")
    is_retryable = False


class RecordAlreadyVerified(BizErrorDefinition):
    """Error definition for attempting to verify an already verified record.

    This error occurs when an operation tries to verify a record that is
    already in a verified state. Verification operations should only be
    performed on unverified records.

    Attributes:
        code: "BIZ:RECORD_ALREADY_VERIFIED"
        http_status: 409 Conflict
        message_template: "Record is already verified."
        is_retryable: False (record state cannot be changed)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(RecordAlreadyVerified())
    """

    code = "BIZ:RECORD_ALREADY_VERIFIED"
    http_status = 409
    message_template = _n("Record is already verified.")
    is_retryable = False


class InvalidStateForVerification(BizErrorDefinition):
    """Error definition for invalid state transitions during verification.

    This error occurs when attempting to verify a record but the requested
    state transition is not allowed from the current state. This ensures
    that verification workflows follow the proper state machine rules.

    Attributes:
        code: "BIZ:INVALID_STATE_FOR_VERIFICATION"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot verify record: transition to '{next_state}' is not allowed from current state."
        is_retryable: False (requires correct state flow)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(InvalidStateForVerification(
        ...     next_state="Active"
        ... ))
    """

    code = "BIZ:INVALID_STATE_FOR_VERIFICATION"
    http_status = 422
    message_template = _n(
        "Cannot verify record: transition to '{next_state}' is not allowed from current state."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        next_state: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes an invalid state for verification error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class TrustLevelElevation(BizErrorDefinition):
    """Error definition for invalid trust level elevation attempts.

    This error occurs when attempting to elevate a trust level to a value
    that is not higher than the current trust level. Trust level elevation
    should only be allowed when the target level is greater than the
    current level.

    Attributes:
        code: "BIZ:TRUST_LEVEL_ELEVATION_ERROR"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot elevate to '{target_level}'. Target level must be higher than current '{current_level}'."
        is_retryable: False (requires valid elevation path)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(TrustLevelElevation(
        ...     target_level="admin",
        ...     current_level="user"
        ... ))
    """

    code = "BIZ:TRUST_LEVEL_ELEVATION_ERROR"
    http_status = 422
    message_template = _n(
        "Cannot elevate to '{target_level}'. Target level must be higher than current '{current_level}'."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        target_level: str | None = None,
        current_level: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a trust level elevation error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class TrustLevelElevationBeyondCore(BizErrorDefinition):
    """Error definition for attempting to elevate trust level beyond CORE.

    This error occurs when attempting to elevate a trust level to a value
    that exceeds the maximum allowed CORE level. Trust level elevation
    is restricted to prevent unauthorized access to the highest privilege
    levels.

    Attributes:
        code: "BIZ:TRUST_LEVEL_ELEVATION_BEYOND_CORE"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot elevate trust level beyond CORE."
        is_retryable: False (elevation not permitted)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(TrustLevelElevationBeyondCore())
    """

    code = "BIZ:TRUST_LEVEL_ELEVATION_BEYOND_CORE"
    http_status = 422
    message_template = _n("Cannot elevate trust level beyond CORE.")
    is_retryable = False


class TrustLevelLoweringBelowUntrusted(BizErrorDefinition):
    """Error definition for attempting to lower trust level below UNTRUSTED.

    This error occurs when attempting to lower a trust level to a value
    that is below the minimum allowed UNTRUSTED level. Trust level lowering
    is restricted to prevent setting trust levels below the system minimum.

    Attributes:
        code: "BIZ:TRUST_LEVEL_LOWERING_BELOW_UNTRUSTED"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot lower trust level below UNTRUSTED."
        is_retryable: False (lowering not permitted)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(TrustLevelLoweringBelowUntrusted())
    """

    code = "BIZ:TRUST_LEVEL_LOWERING_BELOW_UNTRUSTED"
    http_status = 422
    message_template = _n("Cannot lower trust level below UNTRUSTED.")
    is_retryable = False


class TrustLevelLowering(BizErrorDefinition):
    """Error definition for invalid trust level lowering attempts.

    This error occurs when attempting to lower a trust level to a value
    that is not lower than the current trust level. Trust level lowering
    should only be allowed when the target level is less than the current level.

    Attributes:
        code: "BIZ:TRUST_LEVEL_LOWERING_ERROR"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot lower to '{target_level}'. Target level must be lower than current '{current_level}'."
        is_retryable: False (requires valid lowering path)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(TrustLevelLowering(
        ...     target_level="user",
        ...     current_level="admin"
        ... ))
    """

    code = "BIZ:TRUST_LEVEL_LOWERING_ERROR"
    http_status = 422
    message_template = _n(
        "Cannot lower to '{target_level}'. Target level must be lower than current '{current_level}'."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        target_level: str | None = None,
        current_level: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a trust level lowering error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)


class TrustLevelDemotion(BizErrorDefinition):
    """Error definition for invalid trust level demotion attempts.

    This error occurs when attempting to demote a trust level to a target
    level when the current level is already at or below that target level.
    Demotion should only be allowed when the current level is higher than
    the target level.

    Attributes:
        code: "BIZ:TRUST_LEVEL_DEMOTION_ERROR"
        http_status: 422 Unprocessable Entity
        message_template: "Cannot demote from '{current_level}' to {target_level}. Current level is already {target_level} or below."
        is_retryable: False (requires valid demotion path)

    Example:
        >>> # Wrap this definition in a business-specific exception
        ... raise BusinessError(TrustLevelDemotion(
        ...     current_level="REGULAR",
        ...     target_level="REGULAR"
        ... ))
    """

    code = "BIZ:TRUST_LEVEL_DEMOTION_ERROR"
    http_status = 422
    message_template = _n(
        "Cannot demote from '{current_level}' to {target_level}. Current level is already {target_level} or below."
    )
    is_retryable = False

    @overload
    def __init__(
        self,
        message_template: str | None = None,
        /,
        *,
        current_level: str | None = None,
        target_level: str | None = None,
        **kwds,
    ) -> None: ...

    def __init__(self, message_template: str | None = None, /, **kwds):
        """Initializes a trust level demotion error definition.

        Passes all arguments to the parent class constructor.
        """
        super().__init__(message_template, **kwds)
