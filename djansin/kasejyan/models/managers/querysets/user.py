"""QuerySet definitions for user-level lookups in the kasejyan app.

This module exposes :class:`UserQuerySet`, a specialized QuerySet for the
:class:`~djansin.kasejyan.models.User` model. It extends
:class:`~core.models.managers.querysets.BaseUserQuerySet` with reusable,
chainable helpers for filtering users by the presence and creation time of
their related email contact. It is the queryset type referenced by
:class:`~djansin.kasejyan.models.managers.user.UserManager`.
"""

from datetime import datetime
from typing import Self

from core.models.managers.querysets import BaseUserQuerySet


class UserQuerySet(BaseUserQuerySet):
    """QuerySet for the :class:`~djansin.kasejyan.models.User` model.

    Provides chainable filtering helpers scoped to user records and their
    related :class:`~djansin.kasejyan.models.Email` contact. All methods
    return a new QuerySet instance to preserve chaining semantics.

    Attributes:
        Inherited from
        :class:`~core.models.managers.querysets.BaseUserQuerySet`.
    """

    def has_email(self) -> Self:
        """Filter users who have an associated email address.

        Returns:
            Self: A filtered queryset containing only users with a related
            email contact.
        """
        return self.filter(email_address__isnull=False).distinct()

    def has_no_email(self) -> Self:
        """Filter users who have no associated email address.

        Returns:
            Self: A filtered queryset containing only users without a related
            email contact.
        """
        return self.filter(email_address__isnull=True)

    def email_created_before(self, timestamp: datetime) -> Self:
        """Filter users whose email contact was created before a timestamp.

        Args:
            timestamp (datetime): Exclusive upper bound for the email
                contact's ``created_at`` field.

        Returns:
            Self: A filtered queryset containing users whose related email
            was created strictly before ``timestamp``.
        """
        return self.filter(email_address__created_at__lt=timestamp).distinct()

    def email_created_after(self, timestamp: datetime) -> Self:
        """Filter users whose email contact was created after a timestamp.

        Args:
            timestamp (datetime): Exclusive lower bound for the email
                contact's ``created_at`` field.

        Returns:
            Self: A filtered queryset containing users whose related email
            was created strictly after ``timestamp``.
        """
        return self.filter(email_address__created_at__gt=timestamp).distinct()
