"""Provides a base model serializer class combining ModelSerializerMixin with DRF's ModelSerializer.

This module implements a ModelSerializer that serves as a foundation for all
model-based API serializers in the application, incorporating common mixin
functionality while maintaining standard DRF ModelSerializer behavior.
"""

from rest_framework import serializers

from .mixins.model import ModelSerializerMixin


class ModelSerializer(ModelSerializerMixin, serializers.ModelSerializer):
    """A base model serializer that extends Django REST Framework's ModelSerializer.

    This class combines the functionality of ModelSerializerMixin with DRF's
    standard ModelSerializer, providing a consistent foundation for all model-based
    API serializers in the application. It can be extended to add application-wide
    model serializer behaviors such as automatic field filtering, default validation
    rules, or standardized create/update operations.

    Use this base class instead of serializers.ModelSerializer directly to ensure
    all model serializers benefit from shared functionality defined in the mixin.
    """

    ...
