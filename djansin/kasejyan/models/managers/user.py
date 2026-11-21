"""Manager definitions for the :class:`~djansin.kasejyan.models.User` model.

This module exposes :class:`UserManager`, the default manager for the
``User`` model. It binds the model to :class:`UserQuerySet` with an
implicit ``active()`` filter, and provides high-level lookup helpers for
retrieving users by username, email address, or phone number.
"""

from typing import TYPE_CHECKING

from core.models.managers import BaseUserManager
from djansin.kasejyan.models.managers.querysets.user import UserQuerySet


if TYPE_CHECKING:
    from djansin.kasejyan.models import User


class UserManager(BaseUserManager[UserQuerySet]):
    """Manager for the :class:`~djansin.kasejyan.models.User` model.

    Wires the ``User`` model to :class:`UserQuerySet` and exposes
    convenience methods for retrieving active users by their primary
    identifier or by their related contact information. The base queryset
    returned by :meth:`get_queryset` is always scoped to active users via
    the inherited :meth:`~core.models.managers.querysets.BaseUserQuerySet.active`
    filter.

    Attributes:
        Inherited from :class:`~core.models.managers.BaseUserManager`.
    """

    def get_queryset(self) -> UserQuerySet:
        """Return the base queryset for the ``User`` model.

        The returned queryset is pre-filtered to active users only.

        Returns:
            UserQuerySet: An active-user queryset bound to the manager's
            database alias, typed as :class:`UserQuerySet`.
        """
        return UserQuerySet(self.model, using=self._db).active()

    def get_by_username(self, username: str) -> User:
        """Retrieve a single active user by their username.

        Args:
            username (str): The unique username to look up. Comparison is
                exact and case-sensitive as stored in the database.

        Returns:
            User: The matching active :class:`~djansin.kasejyan.models.User`.

        Raises:
            User.DoesNotExist: If no active user with the given username
                exists.
            User.MultipleObjectsReturned: If more than one user matches the
                given username.
        """
        return self.get_queryset().filter(username=username).get()

    def get_by_email(self, address: str) -> User:
        """Retrieve a single active user by their related email address.

        Args:
            address (str): The email address to look up through the related
                :class:`~djansin.kasejyan.models.Email` contact.

        Returns:
            User: The matching active :class:`~djansin.kasejyan.models.User`.

        Raises:
            User.DoesNotExist: If no active user is associated with the given
                email address.
            User.MultipleObjectsReturned: If more than one user matches the
                given email address.
        """
        return self.get_queryset().filter(email__address=address).get()

    def get_by_phone(self, number: str) -> User:
        """Retrieve a single active user by their related phone number.

        Args:
            number (str): The phone number to look up through the related
                :class:`~djansin.kasejyan.models.Phone` contact.

        Returns:
            User: The matching active :class:`~djansin.kasejyan.models.User`.

        Raises:
            User.DoesNotExist: If no active user is associated with the given
                phone number.
            User.MultipleObjectsReturned: If more than one user matches the
                given phone number.
        """
        return self.get_queryset().filter(phone__number=number).get()
