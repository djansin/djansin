"""Base user model implementation extending Django's authentication framework.

This module defines a comprehensive base user model that combines Django's
AbstractBaseUser and PermissionsMixin with the application's BaseModel,
providing a complete user management solution. The model includes standard
user fields, permission management, activity tracking, and convenience
methods for user management operations.

The model uses a custom BaseUserManager that handles user creation, filtering,
and query operations with a focus on active users and identifier-based lookups.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import DateTimeField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.models.base import BaseModel
from core.models.managers.user import BaseUserManager
from core.validators import UsernameValidator


class BaseUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    """A comprehensive base user model for authentication and authorization.

    This abstract model extends Django's AbstractBaseUser and PermissionsMixin
    while incorporating the application's BaseModel features. It provides a
    complete user implementation with username-based authentication, permission
    management, activity tracking, and user management utilities.

    Features:
    - Username-based authentication with custom validation
    - Django's permission framework integration (PermissionsMixin)
    - Automatic timestamp tracking (created_at, updated_at)
    - Public UUID identifier for external references
    - Activity tracking (last_login, password_changed_at)
    - Active/Inactive status management
    - Staff and superuser privilege management
    - Password age tracking and expiration policies

    The model is abstract, serving as a template for concrete user models.
    It uses the USERNAME_FIELD to identify the authentication field (username).

    Attributes:
        objects: The custom BaseUserManager instance bound to this model,
            providing user-specific methods like get_by_identifier(),
            create_user(), create_superuser(), and various counting methods.
        username: A CharField serving as the unique identifier for authentication.
            Validated with custom UsernameValidator enforcing specific character rules.
        is_active: Boolean field indicating whether the user account is active.
            Inactive users cannot log in.
        is_staff: Boolean field granting access to the admin interface.
        is_superuser: Boolean field granting all permissions.
        password_changed_at: DateTimeField tracking when the user last changed
            their password for password expiration policies.
        last_login: DateTimeField tracking the user's last successful authentication.
        date_joined: Property returning created_at for Django compatibility.
        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.
        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
        uuid: UUIDField inherited from BaseModelMixin.
            Public immutable identifier for external references.
    """

    objects: BaseUserManager = BaseUserManager()

    username = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name=_t("Username"),
        validators=[UsernameValidator()],
        help_text=_t(
            "Required. 3-32 characters. Lowercase letters, numbers, and . _ - only."
        ),
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(
        default=True,
        verbose_name=_t("Active"),
        help_text=_t("Designates whether this user should be treated as active."),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_t("Staff status"),
        help_text=_t("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_t("Superuser status"),
        help_text=_t(
            "Designates that this user has all permissions without explicitly assigning them."
        ),
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Password Changed At"),
        help_text=_t("Timestamp when the user last changed their password."),
    )

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Last Login"),
        help_text=_t("Timestamp of the user's last successful login."),
    )

    class Meta:
        """Metadata configuration for BaseUser.

        Makes this model abstract so it doesn't create a database table,
        but provides fields to all inheriting models.
        """

        abstract = True

    @property
    def date_joined(self) -> DateTimeField:
        """Get the date when the user joined.

        This property provides compatibility with Django's default User model,
        allowing seamless integration with code that expects a date_joined field.

        Returns:
            The timestamp when the user was created.
        """
        return self.created_at

    @property
    def last_updated(self) -> DateTimeField:
        """Get the date when the user was last updated.

        This property provides a more intuitive name for the last modification
        timestamp, making it clear when the user record was last changed.

        Returns:
            The timestamp when the user was last updated.
        """
        return self.updated_at

    def activate(self, save: bool = True) -> None:
        """Activate the user account.

        Sets is_active to True, allowing the user to log in.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_active = True
        if save:
            self.save(update_fields=["is_active", "updated_at"])

    def deactivate(self, save: bool = True) -> None:
        """Deactivate the user account.

        Sets is_active to False, preventing the user from logging in.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_active = False
        if save:
            self.save(update_fields=["is_active", "updated_at"])

    def make_staff(self, save: bool = True) -> None:
        """Grant staff privileges to the user.

        Sets is_staff to True, allowing access to the admin interface.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_staff = True
        if save:
            self.save(update_fields=["is_staff", "updated_at"])

    def remove_staff(self, save: bool = True) -> None:
        """Remove staff privileges from the user.

        Sets is_staff to False, revoking admin interface access.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_staff = False
        if save:
            self.save(update_fields=["is_staff", "updated_at"])

    def make_superuser(self, save: bool = True) -> None:
        """Grant superuser privileges to the user.

        Sets is_superuser to True, giving all permissions without explicit assignment.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_superuser = True
        if save:
            self.save(update_fields=["is_superuser", "updated_at"])

    def remove_superuser(self, save: bool = True) -> None:
        """Remove superuser privileges from the user.

        Sets is_superuser to False, removing automatic permission grants.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.is_superuser = False
        if save:
            self.save(update_fields=["is_superuser", "updated_at"])

    def mark_last_login(self, save: bool = True) -> None:
        """Update the last_login timestamp to the current time.

        Should be called on successful user authentication.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.last_login = timezone.now()
        if save:
            self.save(update_fields=["last_login"])

    def get_account_age_days(self) -> int:
        """Calculate the age of the user account in days.

        Returns:
            The number of days since the account was created.
        """
        delta = timezone.now() - self.created_at
        return delta.days

    def get_last_login_days_ago(self) -> int | None:
        """Calculate how many days ago the user last logged in.

        Returns:
            The number of days since last login, or None if the user
            has never logged in.
        """
        if not self.last_login:
            return None
        delta = timezone.now() - self.last_login
        return delta.days

    def is_recently_active(self, days: int = 7) -> bool:
        """Check if the user has been active within the specified number of days.

        Args:
            days: Number of days to consider as "recent". Defaults to 7.

        Returns:
            True if the user has logged in within the specified period,
            False otherwise or if the user has never logged in.
        """
        if not self.last_login:
            return False
        delta = timezone.now() - self.last_login
        return delta.days <= days

    def needs_password_change(self, max_age_days: int = 180) -> bool:
        """Check if the user's password needs to be changed based on age.

        Args:
            max_age_days: Maximum allowed password age in days. Defaults to 180.

        Returns:
            True if the password has exceeded the maximum age,
            False if password_changed_at is not set or within limit.
        """
        if not self.password_changed_at:
            return True
        delta = timezone.now() - self.password_changed_at
        return delta.days > max_age_days
