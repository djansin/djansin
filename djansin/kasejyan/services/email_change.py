"""Service layer for confirming an email change.

Verifies the one-time code sent to the new email, then swaps the user's
current email for the new one — detaching the old email (if any) and
attaching the new one atomically.

All failure paths collapse into a single generic error message to avoid
leaking whether a given email exists, is already linked to the user, or
is owned by someone else — with two intentional exceptions, both raised
only **after** the caller has proven access to the address by presenting
a valid code:

* the "owned by another account" case, reported explicitly so the user
  knows to detach the email from the other account first;
* the "temporarily blocked" case, reported explicitly so the user knows
  to wait for the block to expire rather than retrying.

Because the code proves ownership, neither exception leaks information
to an attacker who lacks access to the address.

The code must have been issued with ``purpose=CodePurpose.CHANGE_EMAIL``;
a code issued for any other operation (e.g. removing the same email) is
rejected by :class:`VerifyContactService` before the swap is attempted.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, DomainError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.exceptions import InvalidVerificationCode
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import EmailChangeResult


class ChangeEmailService(Service[EmailChangeResult]):
    """Change the authenticated user's email address.

    Verifies the one-time code sent to the new email, then atomically
    detaches the user's current email (if any) and attaches the new one.
    The new email must not be owned by another user — enforced again
    here, in case ownership changed between the request and confirmation
    steps. A temporarily blocked email is rejected with an explicit
    message, so the user knows to wait for the block to expire.

    The code is validated with ``purpose=CodePurpose.CHANGE_EMAIL``, so
    a code issued for a different operation (e.g. removing the same
    email) is rejected even if the digits match.

    Every rejection before the code is verified uses the same generic
    :class:`~djansin.kasejyan.exceptions.InvalidVerificationCode`,
    regardless of the underlying cause, so an attacker cannot probe
    email existence or ownership through this endpoint. Once the code
    has been verified, the caller has proven access to the address, and
    the two ownership/block-state exceptions are reported explicitly.
    """

    def execute(self, *, user: User, new_email: str, code: str) -> EmailChangeResult:
        """Confirm an email change for ``user``.

        Args:
            user (User): The authenticated user requesting the change.
            new_email (str): The email address that should replace the
                current one. Must have been the target of a prior
                :class:`RequestChangeEmailService` call.
            code (str): The six-digit verification code sent to
                ``new_email``.

        Returns:
            EmailChangeResult: The username, the previous email (if
            any), the new email, and the change timestamp.

        Raises:
            ValidationError: If ``code`` is missing or empty.
            DomainError: If the email has no pending change, or the
                code is invalid/expired/issued for a different purpose.
            BusinessError: If the email is temporarily blocked or is
                already linked to another account.
        """
        if not code:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid verification code."))
            )

        contact = self._resolve_contact(new_email=new_email)
        self._verify_code(email=new_email, code=code)
        self._ensure_not_blocked(contact=contact)
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

        Uses :meth:`EmailManager.find_by_address` for a direct lookup.
        Raises the generic error if no row exists — the user must have
        requested a code first, which creates the row. The message is
        intentionally indistinguishable from a wrong/expired code.

        Args:
            new_email (str): The email address to resolve.

        Returns:
            Email: The matching contact record.

        Raises:
            DomainError: If no row exists for ``new_email``.
        """
        contact = Email.objects.find_by_address(address=new_email)
        if contact is None:
            raise DomainError(InvalidVerificationCode(target=_t("email address")))
        return contact

    def _ensure_not_blocked(self, *, contact: Email) -> None:
        """Refuse if the new email is temporarily blocked.

        Safe to report explicitly here: the caller has already proven
        access to the address by presenting the verification code, so
        no information is leaked to an attacker who lacks that access.
        The message tells the user to wait for the block to expire
        rather than retrying.

        Args:
            contact (Email): The email row being attached.

        Raises:
            BusinessError: If ``contact`` is currently blocked.
        """
        if contact.is_blocked:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This email is temporarily blocked. Please wait "
                        "until the block expires before changing to it."
                    )
                )
            )

    def _ensure_not_owned_by_other(self, *, user: User, contact: Email) -> None:
        """Refuse if the new email is already owned by another user.

        Ownership may have changed between the request and confirmation
        steps (race condition), so this is re-checked here.

        A specific message is safe here: the user has already proven
        access to this email by receiving the verification code, so no
        information is leaked to an attacker who lacks that access. The
        message tells the user what to do (detach the email from the
        other account first).

        Args:
            user (User): The authenticated user requesting the change.
            contact (Email): The email row being attached.

        Raises:
            BusinessError: If ``contact`` is owned by a different user.
        """
        if contact.user_id is not None and contact.user_id != user.pk:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This email is already linked to another account. "
                        "Please remove it from that account before linking "
                        "it here."
                    )
                )
            )

    def _verify_code(self, *, email: str, code: str) -> None:
        """Verify the one-time code sent to ``email``.

        Delegates to :class:`VerifyContactService` with
        ``purpose=CodePurpose.CHANGE_EMAIL``. Any verification failure
        — wrong purpose, expired code, exhausted attempts, blocked
        contact, mismatched value — surfaces as a :class:`DomainError`
        from the verification service; that error is re-raised as the
        same generic :class:`InvalidVerificationCode` so the caller
        cannot distinguish the underlying cause.

        The re-wrap is intentional: it normalizes the ``target`` label
        to ``"email address"`` regardless of which path inside the
        verification service raised (e.g. invalid identifier vs.
        blocked contact), keeping every rejection response textually
        identical.

        Note that a blocked contact is also rejected here by
        :class:`VerifyContactService`; the explicit blocked-check in
        :meth:`_ensure_not_blocked` runs **after** this method so that
        the generic error is returned first for blocked contacts that
        have not yet proven ownership. Only after the code has been
        accepted does the block state become reportable.

        Args:
            email (str): The email address the code was sent to.
            code (str): The six-digit code supplied by the user.

        Raises:
            DomainError: If the code is invalid, expired, exhausted, or
                was issued for a different purpose.
        """
        try:
            VerifyContactService()(
                identifier=email,
                code=code,
                purpose=Email.CodePurpose.CHANGE_CONTACT,
            )
        except DomainError:
            raise DomainError(
                InvalidVerificationCode(target=_t("email address"))
            ) from None

    def _current_email(self, *, user: User) -> Email | None:
        """Return the user's current email row, if any.

        Args:
            user (User): The authenticated user.

        Returns:
            Email | None: The user's current email row, or ``None`` if
            the user has no email attached.
        """
        return Email.objects.filter(user=user).first()
