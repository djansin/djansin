"""Manager classes providing core and specialized model management capabilities.

This module exports base and specialized Manager classes for common
model operations, including standard management, soft deletion support,
undeletable protection, and user-specific management functionality.

These Managers serve as the foundation for model management throughout
the application, providing consistent and reusable interfaces for
database operations.
"""

from .base import BaseManager
from .soft_deletable import SoftDeletableManager
from .undeletable import UndeletableManager
from .user import BaseUserManager


__all__ = [
    "BaseManager",
    "SoftDeletableManager",
    "UndeletableManager",
    "BaseUserManager",
]
