"""Service layer for removing an email address from a user's account.

Verifies the one-time code sent to the email being removed, ensures the
user retains at least one other login method, detaches the email from
the user, and persists the change atomically. The user instance is
supplied by the view (already authenticated), so no identifier
resolution is needed.

Blocked emails can still be removed: blocking is a temporary throttle
on verification, not a prohibition on detaching the contact. This
matches :class:`RequestRemoveEmailService`, which dispatches codes to
blocked emails.

The code is validated with ``purpose=CodePurpose.REMOVE_EMAIL``, so a
code issued for a different operation (e.g. changing the same email) is
rejected even if the digits match.
"""

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, DomainError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation, OperationNotAllowed
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.exceptions import InvalidVerificationCode
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

    Blocked emails can still be removed: blocking is a temporary
    throttle on verification, not a prohibition on detaching the
    contact. This matches :class:`RequestRemoveEmailService`, which
    dispatches codes to blocked emails.

    The order matters: ownership and code validity are checked first,
    and the "last login method" guard runs only after the caller has
    proven access to the address by presenting the code. This prevents
    an attacker without the code from probing the user's login-method
    inventory through this endpoint.

    Ownership failures collapse into a single generic error, matching
    the request step's behavior, so this endpoint cannot be used to
    enumerate emails or probe ownership.
    """

    def execute(self, *, user: User, email: str, code: str) -> EmailRemovalResult:
        """Confirm the removal of ``email`` from ``user``'s account.

        Args:
            user (User): The authenticated user requesting the removal.
            email (str): The email address to detach. Must belong to
                ``user``. May be currently blocked — blocked emails can
                still be removed.
            code (str): The six-digit verification code sent to
                ``email``.

        Returns:
            EmailRemovalResult: The username, the removed email, and
            the removal timestamp.

        Raises:
            ValidationError: If ``code`` is missing or empty.
            BusinessError: If the email does not belong to the user,
                the code is invalid/expired/issued for a different
                purpose, or the removal would leave the user with no
                login method.
        """
        contact = self._resolve_contact(user=user, email=email)
        self._verify_code(email=email, code=code)
        self._ensure_not_last_credential(user=user)

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

        Deliberately does not distinguish "does not exist" from
        "belongs to another user", to avoid leaking email ownership
        across users. Both cases collapse into the same generic error.

        A blocked email is still resolved — blocking does not prevent
        removal.

        Args:
            user (User): The authenticated user.
            email (str): The email address to resolve.

        Returns:
            Email: The matching contact record.

        Raises:
            BusinessError: If no row exists for ``email`` owned by
                ``user``.
        """
        contact = (
            Email.objects.filter(address=email, user=user)
            .select_related("user")
            .first()
        )

        if contact is None:
            raise BusinessError(
                OperationNotAllowed(
                    reason=_t("The provided email is not owned by the user.")
                )
            )

        return contact

    def _ensure_not_last_credential(self, *, user: User) -> None:
        """Refuse the removal if it would leave the user with no login method.

        A login method is any of: a usable password, a linked phone
        number, or another linked email address. If none of those would
        remain after this email is detached, the operation is rejected.

        Args:
            user (User): The authenticated user.

        Raises:
            BusinessError: If the user would be left with no login
                method after the removal.
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
                        "Cannot remove the last login method. Set a password "
                        "or add a phone number first."
                    )
                )
            )

    def _verify_code(self, *, email: str, code: str) -> None:
        """Verify the one-time code sent to ``email``.

        Delegates to :class:`VerifyContactService` with
        ``purpose=CodePurpose.REMOVE_EMAIL``. Any verification failure
        — wrong purpose, expired code, exhausted attempts, blocked
        contact, mismatched value — surfaces as a :class:`DomainError`
        from the verification service; that error is re-raised as the
        same generic :class:`InvalidVerificationCode` so the caller
        cannot distinguish the underlying cause.

        The re-wrap is intentional: it normalizes the ``target`` label
        to ``"email address"`` regardless of which path inside the
        verification service raised, keeping every rejection response
        textually identical.

        Args:
            email (str): The email address the code was sent to.
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
                identifier=email,
                code=code,
                purpose=Email.CodePurpose.REMOVE_EMAIL,
            )
        except DomainError:
            raise DomainError(
                InvalidVerificationCode(target=_t("email address"))
            ) from None
