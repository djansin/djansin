"""Permission classes for the kasejyan authentication module.

Re-exports the ownership-based permission classes used across the auth
endpoints. Each permission enforces that a user may only act on
resources (emails, phones, sessions) they own, with an ``OrAdmin``
variant that additionally allows staff users.

The ``OrAdmin`` variants are intended for endpoints where support or
administrative staff must be able to act on another user's resource.
The plain variants are intended for endpoints where only the resource
owner should have access.
"""

from .email_ownership import IsEmailOwner, IsEmailOwnerOrAdmin
from .phone_ownership import IsPhoneOwner, IsPhoneOwnerOrAdmin
from .session_ownership import IsSessionOwner, IsSessionOwnerOrAdmin


__all__: list[str] = [
    "IsEmailOwner",
    "IsEmailOwnerOrAdmin",
    "IsPhoneOwner",
    "IsPhoneOwnerOrAdmin",
    "IsSessionOwner",
    "IsSessionOwnerOrAdmin",
]
