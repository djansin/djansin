"""QuerySet classes providing core and specialized query capabilities.

This module exports base and specialized QuerySet classes for common
data access patterns, including standard queries, soft deletion,
undeletable protection, and user-specific filtering.

These QuerySets serve as the foundation for model querying throughout
the application, providing consistent and reusable query interfaces.
"""

from .base import BaseQuerySet
from .soft_deletable import SoftDeletableQuerySet
from .undeletable import UndeletableQuerySet
from .user import BaseUserQuerySet


__all__ = [
    "BaseQuerySet",
    "SoftDeletableQuerySet",
    "UndeletableQuerySet",
    "BaseUserQuerySet",
]
