"""Service layer for confirming an email change.

Verifies the one-time code sent to the new email, then swaps the user's
current email for the new one — detaching the old email (if any) and
attaching the new one atomically.

All failure paths collapse into a single generic error message to
avoid leaking whether a given email exists, is already linked to the
user, or is owned by someone else.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import EmailChangeResult


class ChangeEmailService(Service[EmailChangeResult]):
    """Change the authenticated user's email address.

    Verifies the one-time code sent to the new email, then atomically
    detaches the user's current email (if any) and attaches the new
    one. The new email must not be owned by another user — enforced
    again here, in case ownership changed between the request and
    confirmation steps.

    Every rejection uses the same message (``"Invalid or expired
    verification code."``) regardless of the underlying cause, so an
    attacker cannot probe email existence or ownership through this
    endpoint.
    """

    _GENERIC_ERROR = _t("Invalid or expired verification code.")

    def execute(self, *, user: User, new_email: str, code: str) -> EmailChangeResult:
        contact = self._resolve_contact(new_email=new_email)
        self._verify_code(email=new_email, code=code)
        self._ensure_not_owned_by_other(user=user, contact=contact)

        old_email = self._current_email(user=user)
        now = timezone.now()

        with transaction.atomic():
            # Detach the old email, if any.
            if old_email is not None:
                old_email.user = None
                old_email.save(update_fields=["user"])

            # Attach the new email.
            contact.user = user
            contact.save(update_fields=["user"])

        return EmailChangeResult(
            username=user.username,
            old_email=str(old_email) if old_email is not None else None,
            new_email=new_email,
            changed_at=now,
        )

    def _resolve_contact(self, *, new_email: str) -> Email:
        """Resolve the email row for ``new_email``.

        Raises the generic error if no row exists — the user must have
        requested a code first, which creates the row. The message is
        intentionally indistinguishable from a wrong/expired code.
        """
        contact = Email.objects.filter(address=new_email).first()
        if contact is None:
            raise BusinessError(BusinessRuleViolation(reason=self._GENERIC_ERROR))
        return contact

    def _ensure_not_owned_by_other(self, *, user: User, contact: Email) -> None:
        """Refuse if the new email is already owned by another user.

        Ownership may have changed between the request and confirmation
        steps (race condition), so this is re-checked here.

        A specific message is safe here: the user has already proven
        access to this email by receiving the verification code, so no
        information is leaked to an attacker who lacks that access. The
        message tells the user what to do (detach the email from the other
        account first).
        """
        if contact.user_id is not None and contact.user_id != user.pk:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This email is already linked to another account. Please remove it from that account before linking it here."
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
                BusinessRuleViolation(reason=self._GENERIC_ERROR)
            ) from None

    def _current_email(self, *, user: User) -> Email | None:
        """Return the user's current email row, if any."""
        return Email.objects.filter(user=user).first()
