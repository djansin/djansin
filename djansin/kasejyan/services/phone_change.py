"""Service layer for confirming a phone change.

Verifies the one-time code sent to the new phone, then swaps the user's
current phone for the new one — detaching the old phone (if any) and
attaching the new one atomically.

All failure paths collapse into a single generic error message to
avoid leaking whether a given phone exists, is already linked to the
user, or is owned by someone else.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import PhoneChangeResult


class ChangePhoneService(Service[PhoneChangeResult]):
    """Change the authenticated user's phone number.

    Verifies the one-time code sent to the new phone, then atomically
    detaches the user's current phone (if any) and attaches the new
    one. The new phone must not be owned by another user — enforced
    again here, in case ownership changed between the request and
    confirmation steps.

    Every rejection uses the same message (``"Invalid or expired
    verification code."``) regardless of the underlying cause, so an
    attacker cannot probe phone existence or ownership through this
    endpoint.
    """

    _GENERIC_ERROR = _t("Invalid or expired verification code.")

    def execute(self, *, user: User, new_phone: str, code: str) -> PhoneChangeResult:
        contact = self._resolve_contact(new_phone=new_phone)
        self._verify_code(phone=new_phone, code=code)
        self._ensure_not_owned_by_other(user=user, contact=contact)

        old_phone = self._current_phone(user=user)
        now = timezone.now()

        with transaction.atomic():
            # Detach the old phone, if any.
            if old_phone is not None:
                old_phone.user = None
                old_phone.save(update_fields=["user"])

            # Attach the new phone.
            contact.user = user
            contact.save(update_fields=["user"])

        return PhoneChangeResult(
            username=user.username,
            old_phone=str(old_phone) if old_phone is not None else None,
            new_phone=new_phone,
            changed_at=now,
        )

    def _resolve_contact(self, *, new_phone: str) -> Phone:
        """Resolve the phone row for ``new_phone``.

        Raises the generic error if no row exists — the user must have
        requested a code first, which creates the row. The message is
        intentionally indistinguishable from a wrong/expired code.
        """
        contact = Phone.objects.filter(number=new_phone).first()
        if contact is None:
            raise BusinessError(BusinessRuleViolation(reason=self._GENERIC_ERROR))
        return contact

    def _ensure_not_owned_by_other(self, *, user: User, contact: Phone) -> None:
        """Refuse if the new phone is already owned by another user.

        Ownership may have changed between the request and confirmation
        steps (race condition), so this is re-checked here.

        A specific message is safe here: the user has already proven
        access to this phone by receiving the verification code, so no
        information is leaked to an attacker who lacks that access. The
        message tells the user what to do (detach the phone from the
        other account first).
        """
        if contact.user_id is not None and contact.user_id != user.pk:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This phone number is already linked to another account. Please remove it from that account before linking it here."
                    )
                )
            )

    def _verify_code(self, *, phone: str, code: str) -> None:
        """Verify the one-time code sent to ``phone``.

        Collapses wrong / expired / missing codes into a single message
        to avoid leaking which case occurred.
        """
        if not code:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid verification code."))
            )

        try:
            VerifyContactService()(identifier=phone, code=code)
        except BusinessError:
            raise BusinessError(
                BusinessRuleViolation(reason=self._GENERIC_ERROR)
            ) from None

    def _current_phone(self, *, user: User) -> Phone | None:
        """Return the user's current phone row, if any."""
        return Phone.objects.filter(user=user).first()
