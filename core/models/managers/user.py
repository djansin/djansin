"""User model manager providing comprehensive user management and query utilities.

This module defines a specialized manager class that extends both Django's
BaseUserManager and the application's BaseManager to provide a complete
API for managing user accounts. The manager handles user creation,
filtering, counting, and existence checks with a focus on active users
and role-based queries.

The manager automatically filters out inactive users by default, ensuring
that most queries work with active accounts only, while providing explicit
methods to work with inactive users when needed.
"""

from typing import Generic, TypeVar

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager as DjangoBaseUserManager,
)
from django.utils import timezone

from core.exceptions.app import InvalidFormatError, RequiredFieldError
from core.models.managers.base import BaseManager
from core.models.managers.querysets.user import BaseUserQuerySet


BaseUserQuerySetType = TypeVar("BaseUserQuerySetType", bound="BaseUserQuerySet")


class BaseUserManager(
    BaseManager[BaseUserQuerySetType],
    DjangoBaseUserManager,
    Generic[BaseUserQuerySetType],
):
    """A comprehensive manager for user models with enhanced query capabilities.

    This manager extends Django's BaseUserManager to provide the standard
    user management interface while adding application-specific utilities
    for filtering, counting, and role-based queries.

    Key features:
    - Automatically filters out inactive users from default queries
    - Provides explicit methods to include or target inactive users
    - Supports role-based filtering (staff, superuser, regular, privileged)
    - Implements robust user creation with validation
    - Provides comprehensive counting and existence checks
    - Delegates to BaseUserQuerySet for complex query operations

    The manager is designed to work with custom user models that follow
    Django's authentication conventions and support the standard fields:
    is_active, is_staff, is_superuser, and groups.

    Attributes:
        model: The Django user model class this manager is bound to.
        _db: The database alias this manager uses.
        _queryset_class: The queryset class used for constructing queries.
        _hints: Additional hints for the queryset.
        _built_with: Internal tracking for construction.
    """

    def get_queryset(self) -> BaseUserQuerySet:
        """Return a new QuerySet that automatically filters out inactive users.

        Returns:
            A BaseUserQuerySet instance filtered to only include active users
            (is_active=True).
        """
        return BaseUserQuerySet(self.model, using=self._db).active()

    def include_inactive(self) -> BaseUserQuerySetType:
        """Return a queryset that includes all users, including inactive ones.

        This method provides access to the complete queryset without the
        default active filter, allowing operations on inactive users.

        Returns:
            A queryset containing all users, both active and inactive.
        """
        return self.get_queryset().model._base_manager

    # ========== Query delegation to UserQuerySet ==========

    def active(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include only active users.

        This is the default queryset, explicitly exposed for clarity.

        Returns:
            A queryset containing only users with is_active=True.
        """
        return self.get_queryset()

    def inactive(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include only inactive users.

        Returns:
            A queryset containing only users with is_active=False.
        """
        return self.include_inactive().filter(is_active=False)

    def staff(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include only staff users.

        Returns:
            A queryset containing users with is_staff=True.
        """
        return self.get_queryset().staff()

    def non_staff(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to exclude staff users.

        Returns:
            A queryset containing users with is_staff=False.
        """
        return self.get_queryset().non_staff()

    def superusers(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include only superusers.

        Returns:
            A queryset containing users with is_superuser=True.
        """
        return self.get_queryset().superusers()

    def non_superusers(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to exclude superusers.

        Returns:
            A queryset containing users with is_superuser=False.
        """
        return self.get_queryset().non_superusers()

    def regular_users(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include only regular users.

        Returns:
            A queryset containing users who are neither staff nor superusers.
        """
        return self.get_queryset().regular_users()

    def privileged(self) -> BaseUserQuerySetType:
        """Return a queryset filtered to include privileged users.

        Returns:
            A queryset containing users who are staff or superusers.
        """
        return self.get_queryset().privileged()

    # ========== User creation (overrides) ==========

    def create_user(
        self, username: str, password: str | None = None, **extra_fields
    ) -> AbstractBaseUser:
        """Create a new user with the given username and password.

        Args:
            username: The username for the new user.
            password: Optional password. If not provided, sets an unusable password.
            **extra_fields: Additional fields to set on the user model.

        Returns:
            The newly created user instance.

        Raises:
            RequiredFieldError: If username is empty or required fields are missing.
        """
        if not username:
            raise RequiredFieldError(field="username")

        required_fields = getattr(self.model, "REQUIRED_FIELDS", [])
        missing_fields = [
            field for field in required_fields if field not in extra_fields
        ]
        if missing_fields:
            raise RequiredFieldError(field=f"{', '.join(missing_fields)}")

        user = self.model(username=username, **extra_fields)

        if password:
            user.set_password(password)
            user.password_changed_at = timezone.now()
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, password: str | None = None, **extra_fields
    ) -> AbstractBaseUser:
        """Create a new superuser with staff and superuser privileges.

        Args:
            username: The username for the new superuser.
            password: The password for the superuser.
            **extra_fields: Additional fields to set on the user model.

        Returns:
            The newly created superuser instance.

        Raises:
            InvalidFormatError: If is_staff or is_superuser is not set to True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise InvalidFormatError(expected_format="is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise InvalidFormatError(expected_format="is_superuser=True")

        return self.create_user(username, password, **extra_fields)

    # ========== Count methods ==========

    def count_active(self) -> int:
        """Count the number of active users.

        Returns:
            The total count of users with is_active=True.
        """
        return self.active().count()

    def count_inactive(self) -> int:
        """Count the number of inactive users.

        Returns:
            The total count of users with is_active=False.
        """
        return self.inactive().count()

    def count_staff(self) -> int:
        """Count the number of staff users.

        Returns:
            The total count of users with is_staff=True.
        """
        return self.get_queryset().count_staff()

    def count_superuser(self) -> int:
        """Count the number of superusers.

        Returns:
            The total count of users with is_superuser=True.
        """
        return self.get_queryset().count_superuser()

    def count_regular(self) -> int:
        """Count the number of regular users.

        Returns:
            The total count of users who are neither staff nor superusers.
        """
        return self.get_queryset().count_regular()

    def count_admin_users(self) -> int:
        """Count the number of admin users (staff or superuser).

        Returns:
            The total count of users with is_staff=True or is_superuser=True.
        """
        return self.get_queryset().count_admin_users()

    def count_in_group(self, group_name: str) -> int:
        """Count users in a specific group.

        Args:
            group_name: The name of the group to count.

        Returns:
            The total count of users in the specified group.
        """
        return self.get_queryset().count_in_group(group_name)

    def count_joined_within_days(self, days: int) -> int:
        """Count active users who joined within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of active users who joined in the last `days` days.
        """
        return self.get_queryset().joined_within_days(days).count()

    def count_joined_today(self) -> int:
        """Count active users who joined today.

        Returns:
            The count of active users with date_joined date equal to today.
        """
        return self.get_queryset().joined_today().count()

    def count_logged_in_within_days(self, days: int) -> int:
        """Count active users who last logged in within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of active users with last_login in the last `days` days.
        """
        return self.get_queryset().logged_in_within_days(days).count()

    def count_logged_in_today(self) -> int:
        """Count active users who last logged in today.

        Returns:
            The count of active users with last_login date equal to today.
        """
        return self.get_queryset().logged_in_today().count()

    def count_never_logged_in(self) -> int:
        """Count active users who have never logged in.

        Returns:
            The count of active users with last_login is None.
        """
        return self.get_queryset().never_logged_in().count()

    # ========== Existence checks ==========

    def exists_active(self) -> bool:
        """Check if any active users exist.

        Returns:
            True if at least one active user exists, False otherwise.
        """
        return self.active().exists()

    def exists_staff(self) -> bool:
        """Check if any staff users exist.

        Returns:
            True if at least one staff user exists, False otherwise.
        """
        return self.get_queryset().exists_staff()

    def exists_superuser(self) -> bool:
        """Check if any superusers exist.

        Returns:
            True if at least one superuser exists, False otherwise.
        """
        return self.get_queryset().exists_superuser()

    def exists_username(self, username: str) -> bool:
        """Check if a user with the given username exists.

        Args:
            username: The username to check.

        Returns:
            True if a user with the username exists, False otherwise.
        """
        return self.get_queryset().exists_username(username)
