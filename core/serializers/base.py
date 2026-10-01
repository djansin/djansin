"""Provides a base serializer class that combines BaseSerializerMixin with DRF's Serializer.

This module implements a BaseSerializer that serves as a foundation for all
API serializers in the application, incorporating common mixin functionality
while maintaining standard DRF serializer behavior.
"""

from rest_framework import serializers

from .mixins.base import BaseSerializerMixin


class BaseSerializer(BaseSerializerMixin, serializers.Serializer):
    """A base serializer that extends Django REST Framework's Serializer.

    This class combines the functionality of BaseSerializerMixin with DRF's
    standard Serializer, providing a consistent foundation for all API
    serializers in the application. It can be extended to add application-wide
    serializer behaviors such as custom field representations, standardized
    validation, or common output formatting.

    Use this base class instead of serializers.Serializer directly to ensure
    all serializers benefit from shared functionality defined in the mixin.
    """

    ...
