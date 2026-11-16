"""Service layer for removing an email address from a user's account.

Verifies the one-time code sent to the email being removed, ensures the
user retains at least one other login method, detaches the email from
the user, and persists the change atomically. The user instance is
supplied by the view (already authenticated), so no identifier
resolution is needed.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import EmailRemovalResult


class RemoveEmailService(Service[EmailRemovalResult]):
    """Remove an email address from the authenticated user's account.

    Verifies that the email belongs to the user and that the supplied
    one-time code is valid for it, guards against removing the user's
    last remaining login method (which would lock them out), then
    detaches the email from the user. The email row itself is retained
    with ``user=None`` so the address can be re-attached later without
    losing its history.
    """

    def execute(self, *, user: User, email: str, code: str) -> EmailRemovalResult:
        contact = self._resolve_contact(user=user, email=email)
        self._ensure_not_last_credential(user=user)
        self._verify_code(email=email, code=code)

        now = timezone.now()

        with transaction.atomic():
            contact.user = None
            contact.save(update_fields=["user"])

        return EmailRemovalResult(
            username=user.username,
            removed_email=email,
            removed_at=now,
        )

    def _resolve_contact(self, *, user: User, email: str) -> Email:
        """Resolve the email row owned by ``user``.

        Raises ``ResourceNotFound`` if no such row exists — deliberately
        not distinguishing "does not exist" from "belongs to another
        user", to avoid leaking email ownership across users.
        """
        contact = (
            Email.objects.filter(address=email, user=user)
            .select_related("user")
            .first()
        )

        if contact is None:
            raise BusinessError(ResourceNotFound(resource=_t("Email")))

        return contact

    def _ensure_not_last_credential(self, *, user: User) -> None:
        """Refuse the removal if it would leave the user with no login method.

        A login method is any of: a usable password, a linked phone
        number, or another linked email address. If none of those would
        remain after this email is detached, the operation is rejected.
        """
        has_password = user.has_usable_password()

        has_phone = Phone.objects.filter(user=user).exists()

        # The email being removed still counts in this query; we need
        # at least two so that one remains after removal.
        has_another_email = Email.objects.filter(user=user).count() > 1

        if not (has_password or has_phone or has_another_email):
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "Cannot remove the last login method. Set a password or add a phone number first."
                    )
                )
            )

    def _verify_code(self, *, email: str, code: str) -> None:
        """Verify the one-time code sent to ``email``.

        Collapses wrong / expired / missing codes into a single message
        to avoid leaking which case occurred.
        """
        if not code:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid verification code."))
            )

        try:
            VerifyContactService()(identifier=email, code=code)
        except BusinessError:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Invalid or expired verification code.")
                )
            ) from None
