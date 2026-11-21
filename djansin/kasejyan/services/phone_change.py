"""Service layer for confirming a phone change.

Verifies the one-time code sent to the new phone, then swaps the user's
current phone for the new one — detaching the old phone (if any) and
attaching the new one atomically.

All failure paths collapse into a single generic error message to avoid
leaking whether a given phone exists, is already linked to the user, or
is owned by someone else — with two intentional exceptions, both raised
only **after** the caller has proven access to the number by presenting
a valid code:

* the "owned by another account" case, reported explicitly so the user
  knows to detach the phone from the other account first;
* the "temporarily blocked" case, reported explicitly so the user knows
  to wait for the block to expire rather than retrying.

Because the code proves ownership, neither exception leaks information
to an attacker who lacks access to the number.

The code must have been issued with ``purpose=CodePurpose.CHANGE_PHONE``;
a code issued for any other operation (e.g. removing the same phone) is
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
from djansin.kasejyan.models import Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import PhoneChangeResult


class ChangePhoneService(Service[PhoneChangeResult]):
    """Change the authenticated user's phone number.

    Verifies the one-time code sent to the new phone, then atomically
    detaches the user's current phone (if any) and attaches the new one.
    The new phone must not be owned by another user — enforced again
    here, in case ownership changed between the request and confirmation
    steps. A temporarily blocked phone is rejected with an explicit
    message, so the user knows to wait for the block to expire.

    The code is validated with ``purpose=CodePurpose.CHANGE_PHONE``, so
    a code issued for a different operation (e.g. removing the same
    phone) is rejected even if the digits match.

    Every rejection before the code is verified uses the same generic
    :class:`~djansin.kasejyan.exceptions.InvalidVerificationCode`,
    regardless of the underlying cause, so an attacker cannot probe
    phone existence or ownership through this endpoint. Once the code
    has been verified, the caller has proven access to the number, and
    the two ownership/block-state exceptions are reported explicitly.
    """

    def execute(self, *, user: User, new_phone: str, code: str) -> PhoneChangeResult:
        """Confirm a phone change for ``user``.

        Args:
            user (User): The authenticated user requesting the change.
            new_phone (str): The phone number that should replace the
                current one. Must have been the target of a prior
                :class:`RequestChangePhoneService` call.
            code (str): The six-digit verification code sent to
                ``new_phone``.

        Returns:
            PhoneChangeResult: The username, the previous phone (if
            any), the new phone, and the change timestamp.

        Raises:
            ValidationError: If ``code`` is missing or empty.
            DomainError: If the phone has no pending change, or the
                code is invalid/expired/issued for a different purpose.
            BusinessError: If the phone is temporarily blocked or is
                already linked to another account.
        """
        if not code:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid verification code."))
            )

        contact = self._resolve_contact(new_phone=new_phone)
        self._verify_code(phone=new_phone, code=code)
        self._ensure_not_blocked(contact=contact)
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

        Uses :meth:`PhoneManager.find_by_number` for a direct lookup.
        Raises the generic error if no row exists — the user must have
        requested a code first, which creates the row. The message is
        intentionally indistinguishable from a wrong/expired code.

        Args:
            new_phone (str): The phone number to resolve.

        Returns:
            Phone: The matching contact record.

        Raises:
            DomainError: If no row exists for ``new_phone``.
        """
        contact = Phone.objects.find_by_number(number=new_phone)
        if contact is None:
            raise DomainError(InvalidVerificationCode(target=_t("phone number")))
        return contact

    def _ensure_not_blocked(self, *, contact: Phone) -> None:
        """Refuse if the new phone is temporarily blocked.

        Safe to report explicitly here: the caller has already proven
        access to the number by presenting the verification code, so no
        information is leaked to an attacker who lacks that access. The
        message tells the user to wait for the block to expire rather
        than retrying.

        Args:
            contact (Phone): The phone row being attached.

        Raises:
            BusinessError: If ``contact`` is currently blocked.
        """
        if contact.is_blocked:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This phone number is temporarily blocked. Please wait "
                        "until the block expires before changing to it."
                    )
                )
            )

    def _ensure_not_owned_by_other(self, *, user: User, contact: Phone) -> None:
        """Refuse if the new phone is already owned by another user.

        Ownership may have changed between the request and confirmation
        steps (race condition), so this is re-checked here.

        A specific message is safe here: the user has already proven
        access to this phone by receiving the verification code, so no
        information is leaked to an attacker who lacks that access. The
        message tells the user what to do (detach the phone from the
        other account first).

        Args:
            user (User): The authenticated user requesting the change.
            contact (Phone): The phone row being attached.

        Raises:
            BusinessError: If ``contact`` is owned by a different user.
        """
        if contact.user_id is not None and contact.user_id != user.pk:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "This phone number is already linked to another account. "
                        "Please remove it from that account before linking "
                        "it here."
                    )
                )
            )

    def _verify_code(self, *, phone: str, code: str) -> None:
        """Verify the one-time code sent to ``phone``.

        Delegates to :class:`VerifyContactService` with
        ``purpose=CodePurpose.CHANGE_PHONE``. Any verification failure
        — wrong purpose, expired code, exhausted attempts, blocked
        contact, mismatched value — surfaces as a :class:`DomainError`
        from the verification service; that error is re-raised as the
        same generic :class:`InvalidVerificationCode` so the caller
        cannot distinguish the underlying cause.

        The re-wrap is intentional: it normalizes the ``target`` label
        to ``"phone number"`` regardless of which path inside the
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
            phone (str): The phone number the code was sent to.
            code (str): The six-digit code supplied by the user.

        Raises:
            ValidationError: If ``code`` is missing or empty.
            DomainError: If the code is invalid, expired, exhausted, or
                was issued for a different purpose.
        """
        if not code:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid verification code."))
            )

        try:
            VerifyContactService()(
                identifier=phone,
                code=code,
                purpose=Phone.CodePurpose.CHANGE_CONTACT,
            )
        except DomainError:
            raise DomainError(
                InvalidVerificationCode(target=_t("phone number"))
            ) from None

    def _current_phone(self, *, user: User) -> Phone | None:
        """Return the user's current phone row, if any.

        Args:
            user (User): The authenticated user.

        Returns:
            Phone | None: The user's current phone row, or ``None`` if
            the user has no phone attached.
        """
        return Phone.objects.filter(user=user).first()
