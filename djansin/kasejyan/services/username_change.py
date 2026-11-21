"""Service layer for changing a user's username.

Validates the new username's format, ensures global uniqueness, and
persists the change atomically. The user instance is supplied by the
view (already authenticated), so no identifier resolution is needed.
"""

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    DuplicateResource,
)
from core.exceptions.errors.validation import InvalidUsername
from core.services import Service
from core.utils.user_identifier import (
    collect_username_errors,
    is_valid_username,
)
from djansin.kasejyan.models import User
from djansin.kasejyan.types import UsernameChangeResult


class ChangeUsernameService(Service[UsernameChangeResult]):
    """Change the username of an authenticated user.

    Verifies that the new username differs from the current one, that
    it satisfies the project's identifier format rules, and that it is
    not already taken. The change is persisted atomically, with a
    database-level uniqueness check as the final safeguard against
    race conditions.
    """

    def execute(self, *, user: User, new_username: str) -> UsernameChangeResult:
        """Change ``user``'s username to ``new_username``.

        Args:
            user (User): The authenticated user changing their
                username.
            new_username (str): The desired new username. Must satisfy
                the project's identifier format rules and not already
                be taken.

        Returns:
            UsernameChangeResult: The old and new usernames, and the
            change timestamp.

        Raises:
            BusinessError: If ``new_username`` equals the current
                username, fails the identifier format rules, or is
                already taken by another user.
        """
        old_username = user.username

        if new_username == old_username:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("New username must differ from the current username.")
                )
            )

        if not is_valid_username(username=new_username):
            errors = collect_username_errors(new_username)
            raise BusinessError(InvalidUsername(field_errors=errors))

        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            raise BusinessError(
                DuplicateResource(resource=_t("User"), field_name=_t("username"))
            )

        now = timezone.now()

        try:
            with transaction.atomic():
                user.username = new_username
                user.save(update_fields=["username"])
        except IntegrityError as exc:
            raise BusinessError(
                DuplicateResource(resource=_t("User"), field_name=_t("username"))
            ) from exc

        return UsernameChangeResult(
            old_username=old_username,
            new_username=new_username,
            changed_at=now,
        )
