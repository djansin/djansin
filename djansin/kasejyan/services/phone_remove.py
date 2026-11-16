"""Service layer for removing a phone number from a user's account.

Verifies the one-time code sent to the phone being removed, ensures the
user retains at least one other login method, detaches the phone from
the user, and persists the change atomically. The user instance is
supplied by the view (already authenticated), so no identifier
resolution is needed.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.services import Service
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import PhoneRemovalResult


class RemovePhoneService(Service[PhoneRemovalResult]):
    """Remove a phone number from the authenticated user's account.

    Verifies that the phone belongs to the user and that the supplied
    one-time code is valid for it, guards against removing the user's
    last remaining login method (which would lock them out), then
    detaches the phone from the user. The phone row itself is retained
    with ``user=None`` so the number can be re-attached later without
    losing its history.
    """

    def execute(self, *, user: User, phone: str, code: str) -> PhoneRemovalResult:
        contact = self._resolve_contact(user=user, phone=phone)
        self._ensure_not_last_credential(user=user)
        self._verify_code(phone=phone, code=code)

        now = timezone.now()

        with transaction.atomic():
            contact.user = None
            contact.save(update_fields=["user"])

        return PhoneRemovalResult(
            username=user.username,
            removed_phone=phone,
            removed_at=now,
        )

    def _resolve_contact(self, *, user: User, phone: str) -> Phone:
        """Resolve the phone row owned by ``user``.

        Raises ``ResourceNotFound`` if no such row exists — deliberately
        not distinguishing "does not exist" from "belongs to another
        user", to avoid leaking phone ownership across users.
        """
        contact = (
            Phone.objects.filter(number=phone, user=user).select_related("user").first()
        )

        if contact is None:
            raise BusinessError(ResourceNotFound(resource=_t("Phone")))

        return contact

    def _ensure_not_last_credential(self, *, user: User) -> None:
        """Refuse the removal if it would leave the user with no login method.

        A login method is any of: a usable password, another linked
        phone number, or a linked email address. If none of those would
        remain after this phone is detached, the operation is rejected.
        """
        has_password = user.has_usable_password()

        has_email = Email.objects.filter(user=user).exists()

        # The phone being removed still counts in this query; we need
        # at least two so that one remains after removal.
        has_another_phone = Phone.objects.filter(user=user).count() > 1

        if not (has_password or has_email or has_another_phone):
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "Cannot remove the last login method. Set a password or add an email address first."
                    )
                )
            )

    def _verify_code(self, *, phone: str, code: str) -> None:
        """Verify the one-time code sent to ``phone``.

        Collapses wrong / expired / missing codes into a single message
        to avoid leaking which case occurred.
        """
        if not code:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Verification code is required."))
            )

        try:
            VerifyContactService()(identifier=phone, code=code)
        except BusinessError:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Invalid or expired verification code.")
                )
            ) from None
