"""Core model classes providing the foundation for application models.

This module exports base model classes that combine various mixins and
functionalities to serve as the foundation for all application models.
These include timestamp tracking, UUID identification, soft deletion,
undeletable protection, and user model implementations.

The models are organized in a hierarchy from abstract to concrete,
allowing flexibility in choosing the appropriate base class for
different use cases.
"""

from .abstract import AbstractModel
from .base import BaseModel
from .soft_deletable import SoftDeletableModel
from .undeletable import UndeletableModel
from .user import BaseUser


__all__ = [
    "AbstractModel",
    "BaseModel",
    "SoftDeletableModel",
    "UndeletableModel",
    "BaseUser",
]
