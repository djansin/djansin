"""Serializer definitions for exposing user account data.

This module defines :class:`UserSerializer`, a read-oriented model
serializer that renders the public representation of a
:class:`~djansin.kasejyan.models.User` instance for API responses.
"""

from core.serializers import ModelSerializer
from djansin.kasejyan.models import User


class UserSerializer(ModelSerializer):
    """Model serializer exposing the public representation of a user.

    Serializes a :class:`~djansin.kasejyan.models.User` into a minimal,
    externally safe payload. The ``uuid``, ``is_active``, and
    ``date_joined`` fields are marked read-only so they cannot be modified
    through this serializer; only ``username`` remains writable by default.

    Attributes:
        Meta (type): Serializer configuration binding this serializer to the
            :class:`~djansin.kasejyan.models.User` model and declaring
            the exposed and read-only fields.
    """

    class Meta:
        """Serializer metadata for :class:`UserSerializer`."""

        model = User
        fields = ["uuid", "username", "is_active", "date_joined"]
        read_only_fields = ["uuid", "is_active", "date_joined"]
