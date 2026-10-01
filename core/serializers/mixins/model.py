"""Provides a model serializer mixin that extends BaseSerializerMixin.

This module implements a ModelSerializerMixin that adds common functionality
for Django REST Framework ModelSerializers, serving as a foundation for
reusable model serializer behaviors.
"""

from .base import BaseSerializerMixin


class ModelSerializerMixin(BaseSerializerMixin):
    """A mixin for Django REST Framework ModelSerializers.

    This mixin extends BaseSerializerMixin and is designed to be used with
    ModelSerializer classes. It can be extended to add shared functionality
    such as automatic field exclusion, default validation rules, or
    standardized create/update behaviors across multiple model serializers.
    """

    ...
