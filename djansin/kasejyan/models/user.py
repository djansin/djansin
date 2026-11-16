"""Model definition for the :class:`User` account entity.

This module defines :class:`User`, the concrete user model for the
kasejyan application. It extends :class:`~core.models.BaseUser`
(which supplies kasejyan-related fields and permissions) and is
managed by :class:`~djansin.kasejyan.models.managers.user.UserManager`.
"""

from django.utils.translation import gettext_lazy as _t

from core.models import BaseUser

from .managers.user import UserManager


class User(BaseUser):
    """Concrete user model for the kasejyan application.

    Inherits all fields and behavior from :class:`~core.models.BaseUser`,
    including credentials, activation state, staff/superuser flags, and
    permission relations. The model is bound to
    :class:`~djansin.kasejyan.models.managers.user.UserManager`, which
    scopes queries to active users and exposes identifier-based lookups.

    Attributes:
        objects (UserManager): Default manager bound to
            :class:`~djansin.kasejyan.models.managers.user.UserManager`.
        Meta: Django model options, including the human-readable singular
            and plural names.
    """

    objects: UserManager = UserManager()

    class Meta:
        """Django model metadata for :class:`User`."""

        verbose_name = _t("User")
        verbose_name_plural = _t("Users")
