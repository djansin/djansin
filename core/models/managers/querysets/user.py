"""User query set implementation providing comprehensive user filtering and query utilities.

This module defines a specialized query set class for user models with extensive
filtering capabilities. It provides methods for username-based filtering, status
queries, group memberships, authentication status, time-based user activity
tracking, and various existence and counting utilities.

The query set is designed to work with Django's User model or custom user models
that include standard fields: username, is_active, is_staff, is_superuser,
date_joined, last_login, and groups.
"""

from datetime import datetime
from typing import Self

from django.db.models import Q
from django.utils import timezone

from core.models.managers.querysets.base import BaseQuerySet


class BaseUserQuerySet(BaseQuerySet):
    """A specialized query set for user models with comprehensive user-specific queries.

    This query set extends BaseQuerySet with methods specifically designed for
    querying user data. It provides convenient filters for common user-related
    queries including username lookups, status filtering, group memberships,
    authentication status, and user activity patterns.

    The class provides extensive filtering capabilities organized into categories:
    - Username-based filtering (by_username, username_contains, etc.)
    - Status-based filtering (active, staff, superuser, regular)
    - Combined status filters (active_staff, privileged, etc.)
    - Group-based filtering (in_group, has_no_groups, etc.)
    - Authentication status (with_unusable_password, with_set_password)
    - Time-based user activity (joined_*, logged_in_*, etc.)
    - Ordering utilities (order_by_username, order_by_privilege, etc.)
    - Existence checks and counting methods

    Attributes:
        model: The Django user model class this query set is bound to.
        query: The underlying SQL query object.
        _result_cache: Cached results from the database.
        _sticky_filter: Internal flag for filter stickiness.
    """

    # ========== Username-based filtering ==========

    def by_username(self, username: str) -> Self:
        """Filter users by a single username (exact match).

        Args:
            username: The username string to filter by.

        Returns:
            A filtered queryset containing users with the specified username.
        """
        return self.filter(username=username)

    def by_usernames(self, usernames: list[str]) -> Self:
        """Filter users by a list of usernames.

        Args:
            usernames: A list of username strings to filter by.

        Returns:
            A filtered queryset containing users with usernames in the given list.
        """
        return self.filter(username__in=usernames)

    def username_contains(self, substring: str) -> Self:
        """Filter users whose username contains a substring (case-insensitive).

        Args:
            substring: The substring to search for in usernames.

        Returns:
            A filtered queryset containing users with usernames containing
            the specified substring.
        """
        return self.filter(username__icontains=substring)

    def username_startswith(self, prefix: str) -> Self:
        """Filter users whose username starts with a prefix (case-insensitive).

        Args:
            prefix: The prefix to match at the start of usernames.

        Returns:
            A filtered queryset containing users with usernames starting with
            the specified prefix.
        """
        return self.filter(username__istartswith=prefix)

    def username_endswith(self, suffix: str) -> Self:
        """Filter users whose username ends with a suffix (case-insensitive).

        Args:
            suffix: The suffix to match at the end of usernames.

        Returns:
            A filtered queryset containing users with usernames ending with
            the specified suffix.
        """
        return self.filter(username__iendswith=suffix)

    # ========== Status-based filtering ==========

    def active(self) -> Self:
        """Filter the queryset to include only active users.

        Returns:
            A filtered queryset containing users with is_active=True.
        """
        return self.filter(is_active=True)

    def staff(self) -> Self:
        """Filter the queryset to include only staff users.

        Returns:
            A filtered queryset containing users with is_staff=True.
        """
        return self.filter(is_staff=True)

    def non_staff(self) -> Self:
        """Filter the queryset to exclude staff users.

        Returns:
            A filtered queryset containing users with is_staff=False.
        """
        return self.filter(is_staff=False)

    def superusers(self) -> Self:
        """Filter the queryset to include only superusers.

        Returns:
            A filtered queryset containing users with is_superuser=True.
        """
        return self.filter(is_superuser=True)

    def non_superusers(self) -> Self:
        """Filter the queryset to exclude superusers.

        Returns:
            A filtered queryset containing users with is_superuser=False.
        """
        return self.filter(is_superuser=False)

    def regular_users(self) -> Self:
        """Filter the queryset to include only regular (non-staff, non-superuser) users.

        Returns:
            A filtered queryset containing users who are neither staff nor superusers.
        """
        return self.non_staff().non_superusers()

    # ========== Combined status filters ==========

    def staff_or_superuser(self) -> Self:
        """Filter the queryset to include users who are either staff or superusers.

        Returns:
            A filtered queryset containing users with is_staff=True or is_superuser=True.
        """
        return self.filter(Q(is_staff=True) | Q(is_superuser=True))

    def privileged(self) -> Self:
        """Alias for staff_or_superuser to identify privileged users.

        Returns:
            A filtered queryset containing privileged users.
        """
        return self.staff_or_superuser()

    def active_privileged(self) -> Self:
        """Filter active privileged users (staff or superuser).

        Returns:
            A filtered queryset containing active users who are staff or superusers.
        """
        return self.active().privileged()

    def active_staff(self) -> Self:
        """Filter active staff users.

        Returns:
            A filtered queryset containing users with is_active=True and is_staff=True.
        """
        return self.active().staff()

    def active_superuser(self) -> Self:
        """Filter active superusers.

        Returns:
            A filtered queryset containing users with is_active=True and is_superuser=True.
        """
        return self.active().superusers()

    def active_regular(self) -> Self:
        """Filter active regular users.

        Returns:
            A filtered queryset containing active users who are neither staff nor superusers.
        """
        return self.active().regular_users()

    # ========== Group-based filtering ==========

    def in_group(self, group_name: str) -> Self:
        """Filter users belonging to a specific group by name.

        Args:
            group_name: The name of the group to filter by.

        Returns:
            A filtered queryset containing users in the specified group.
        """
        return self.filter(groups__name=group_name)

    def in_any_group(self, group_names: list[str]) -> Self:
        """Filter users belonging to any of the specified groups by name.

        Args:
            group_names: A list of group names to filter by.

        Returns:
            A filtered queryset containing users in any of the specified groups.
        """
        return self.filter(groups__name__in=group_names)

    def in_group_by_id(self, group_id: int) -> Self:
        """Filter users belonging to a specific group by ID.

        Args:
            group_id: The ID of the group to filter by.

        Returns:
            A filtered queryset containing users in the specified group.
        """
        return self.filter(groups__id=group_id)

    def in_any_group_by_id(self, group_ids: list[int]) -> Self:
        """Filter users belonging to any of the specified groups by ID.

        Args:
            group_ids: A list of group IDs to filter by.

        Returns:
            A filtered queryset containing users in any of the specified groups.
        """
        return self.filter(groups__id__in=group_ids)

    def has_no_groups(self) -> Self:
        """Filter users who are not members of any group.

        Returns:
            A filtered queryset containing users with no group memberships.
        """
        return self.filter(groups__isnull=True)

    # ========== Combined user type filters ==========

    def admin_users(self) -> Self:
        """Filter users with administrative privileges (staff or superuser).

        Returns:
            A filtered queryset containing users with is_staff=True or is_superuser=True.
        """
        return self.staff_or_superuser()

    def active_admin_users(self) -> Self:
        """Filter active users with administrative privileges.

        Returns:
            A filtered queryset containing active users who are staff or superusers.
        """
        return self.active().admin_users()

    def superusers_with_staff(self) -> Self:
        """Filter superusers who also have staff status.

        Returns:
            A filtered queryset containing users with both is_superuser=True and is_staff=True.
        """
        return self.superusers().staff()

    # ========== Authentication status ==========

    def with_unusable_password(self) -> Self:
        """Filter users who have unusable passwords (e.g., social auth users).

        Returns:
            A filtered queryset of users whose password field starts with '!'.
        """
        return self.filter(password__startswith="!")

    def with_set_password(self) -> Self:
        """Filter users who have usable passwords.

        Returns:
            A filtered queryset of users whose password field does not start with '!'.
        """
        return self.exclude(password__startswith="!")

    # ========== Time-based user queries ==========

    def joined_before(self, timestamp: datetime) -> Self:
        """Filter users who joined before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Users created before this time
                will be included.

        Returns:
            A filtered queryset of users with date_joined < timestamp.
        """
        return self.created_before(timestamp)

    def joined_after(self, timestamp: datetime) -> Self:
        """Filter users who joined after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Users created after this time
                will be included.

        Returns:
            A filtered queryset of users with date_joined > timestamp.
        """
        return self.created_after(timestamp)

    def joined_between(self, start: datetime, end: datetime) -> Self:
        """Filter users who joined within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset of users with date_joined between start and end.
        """
        return self.created_between(start, end)

    def joined_within_days(self, days: int) -> Self:
        """Filter users who joined within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset of users who joined in the last `days` days.
        """
        return self.created_within_days(days)

    def joined_today(self) -> Self:
        """Filter users who joined today.

        Returns:
            A filtered queryset of users with date_joined date equal to today.
        """
        return self.created_today()

    # ========== Last login queries ==========

    def logged_in_before(self, timestamp: datetime) -> Self:
        """Filter users who last logged in before a specific timestamp.

        Args:
            timestamp: The datetime threshold. Users with last_login < timestamp
                will be included.

        Returns:
            A filtered queryset of users with last_login < timestamp.
        """
        return self.filter(last_login__lt=timestamp)

    def logged_in_after(self, timestamp: datetime) -> Self:
        """Filter users who last logged in after a specific timestamp.

        Args:
            timestamp: The datetime threshold. Users with last_login > timestamp
                will be included.

        Returns:
            A filtered queryset of users with last_login > timestamp.
        """
        return self.filter(last_login__gt=timestamp)

    def logged_in_between(self, start: datetime, end: datetime) -> Self:
        """Filter users who last logged in within a datetime range (inclusive).

        Args:
            start: The start datetime (inclusive).
            end: The end datetime (inclusive).

        Returns:
            A filtered queryset of users with last_login between start and end.
        """
        return self.filter(last_login__gte=start, last_login__lte=end)

    def logged_in_within_days(self, days: int) -> Self:
        """Filter users who last logged in within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            A filtered queryset of users with last_login in the last `days` days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(last_login__gte=cutoff)

    def logged_in_today(self) -> Self:
        """Filter users who last logged in today.

        Returns:
            A filtered queryset of users with last_login date equal to today.
        """
        today = timezone.now().date()
        return self.filter(last_login__date=today)

    def never_logged_in(self) -> Self:
        """Filter users who have never logged in.

        Returns:
            A filtered queryset of users with last_login is None.
        """
        return self.filter(last_login__isnull=True)

    # ========== Ordering ==========

    def order_by_username(self, descending: bool = False) -> Self:
        """Order users by username.

        Args:
            descending: If True, order descending (Z to A). Defaults to False.

        Returns:
            An ordered queryset by username.
        """
        order = "-username" if descending else "username"
        return self.order_by(order)

    def order_by_activity(self, active_first: bool = True) -> Self:
        """Order users by activity status.

        Args:
            active_first: If True, active users first. Defaults to True.

        Returns:
            An ordered queryset by is_active.
        """
        order = "-is_active" if active_first else "is_active"
        return self.order_by(order)

    def order_by_privilege(self, privileged_first: bool = True) -> Self:
        """Order users by privilege level.

        Args:
            privileged_first: If True, superusers first, then staff. Defaults to True.

        Returns:
            An ordered queryset by is_superuser and is_staff.
        """
        # Order by is_superuser first (highest privilege), then is_staff
        order = "-is_superuser" if privileged_first else "is_superuser"
        return self.order_by(order, "is_staff")

    # ========== Existence checks ==========

    def exists_active(self) -> bool:
        """Check if any active users exist.

        Returns:
            True if at least one active user exists, False otherwise.
        """
        return self.active().exists()

    def exists_regular(self) -> bool:
        """Check if any regular users exist.

        Returns:
            True if at least one regular user exists, False otherwise.
        """
        return self.regular().exists()

    def exists_username(self, username: str) -> bool:
        """Check if a user with a specific username exists.

        Args:
            username: The username to check.

        Returns:
            True if a user with the username exists, False otherwise.
        """
        return self.by_username(username).exists()

    def exists_in_group(self, group_name: str) -> bool:
        """Check if any users exist in a specific group.

        Args:
            group_name: The name of the group to check.

        Returns:
            True if at least one user is in the group, False otherwise.
        """
        return self.in_group(group_name).exists()

    def exists_staff(self) -> bool:
        """Check if any staff users exist.

        Returns:
            True if at least one staff user exists, False otherwise.
        """
        return self.staff().exists()

    def exists_superuser(self) -> bool:
        """Check if any superusers exist.

        Returns:
            True if at least one superuser exists, False otherwise.
        """
        return self.superusers().exists()

    def exists_regular_user(self) -> bool:
        """Check if any regular users exist.

        Returns:
            True if at least one regular user exists, False otherwise.
        """
        return self.regular_users().exists()

    # ========== Count methods ==========

    def count_active(self) -> int:
        """Count active users.

        Returns:
            Number of active users.
        """
        return self.active().count()

    def count_superuser(self) -> int:
        """Count superusers.

        Returns:
            Number of superusers.
        """
        return self.superuser().count()

    def count_regular(self) -> int:
        """Count regular users.

        Returns:
            Number of regular users.
        """
        return self.regular().count()

    def count_active_staff(self) -> int:
        """Count active staff users.

        Returns:
            Number of active staff users.
        """
        return self.active_staff().count()

    def count_active_superuser(self) -> int:
        """Count active superusers.

        Returns:
            Number of active superusers.
        """
        return self.active_superuser().count()

    def count_admin_users(self) -> int:
        """Count admin users (staff or superuser).

        Returns:
            Number of admin users.
        """
        return self.admin_users().count()

    def count_in_group(self, group_name: str) -> int:
        """Count users in a specific group.

        Args:
            group_name: The name of the group.

        Returns:
            Number of users in the group.
        """
        return self.in_group(group_name).count()

    def count_staff(self) -> int:
        """Count the number of staff users.

        Returns:
            The total number of staff users.
        """
        return self.staff().count()

    def count_superusers(self) -> int:
        """Count the number of superusers.

        Returns:
            The total number of superusers.
        """
        return self.superusers().count()

    def count_regular_users(self) -> int:
        """Count the number of regular users.

        Returns:
            The total number of regular (non-staff, non-superuser) users.
        """
        return self.regular_users().count()

    def count_joined_within_days(self, days: int) -> int:
        """Count users who joined within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of users who joined in the last `days` days.
        """
        return self.joined_within_days(days).count()

    def count_joined_today(self) -> int:
        """Count users who joined today.

        Returns:
            The count of users with date_joined date equal to today.
        """
        return self.joined_today().count()

    def count_logged_in_within_days(self, days: int) -> int:
        """Count users who last logged in within the last N days.

        Args:
            days: The number of days to look back from the current time.

        Returns:
            The count of users with last_login in the last `days` days.
        """
        return self.logged_in_within_days(days).count()

    def count_logged_in_today(self) -> int:
        """Count users who last logged in today.

        Returns:
            The count of users with last_login date equal to today.
        """
        return self.logged_in_today().count()

    def count_never_logged_in(self) -> int:
        """Count users who have never logged in.

        Returns:
            The count of users with last_login is None.
        """
        return self.never_logged_in().count()
