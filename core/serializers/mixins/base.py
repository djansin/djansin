"""Provides a base serializer mixin with common functionality for DRF serializers.

This module implements a BaseSerializerMixin that can be extended by other
serializer mixins or used directly to add shared capabilities such as
field customization, validation helpers, or standardized representations.
"""

from typing import Any

from core.exceptions.frameworks import DrfInputError, ValidErrorDefinition


class BaseSerializerMixin:
    """A base mixin for Django REST Framework serializers.

    This mixin serves as a foundation for creating reusable serializer
    behaviors. It can be extended to add common functionality such as
    dynamic field selection, custom field representations, or standardized
    validation patterns across multiple serializers.

    The mixin is intentionally minimal to allow for flexible extension
    without imposing unwanted defaults.
    """

    def raise_input_error(
        self, error: str | ValidErrorDefinition, **context: Any
    ) -> None:
        """Raises an :class:`InputError` with the given error and context.

        Args:
            error: An error message or a :class:`ValidErrorDefinition`
                describing the failure.
            **context: Additional keyword arguments attached to the error
                payload (for example, field name or expected length).

        Raises:
            DrfInputError: Always.
        """
        raise DrfInputError(error, **context)
