"""Service layer for requesting an email-change verification code.

Dispatches a fresh one-time code to the target email without revealing
whether the address is already linked to any account. Ownership is
decided at confirmation time, once the caller has proven access to the
address by presenting the code. This is the first step of the two-step
email-change flow; the second step is handled by
:class:`ChangeEmailService`.

Contacts that are temporarily blocked are treated like any other
address: a generic success response is returned, without revealing
that the address exists but is blocked.

The code is issued with ``purpose=CodePurpose.CHANGE_EMAIL``, so it
cannot be replayed for a different operation (e.g. removing the same
email).
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils.user_identifier import is_valid_email
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.models.mixins.verifiable import DEFAULT_CODE_TTL_MINUTES
from djansin.kasejyan.types import EmailChangeRequestResult


class RequestChangeEmailService(Service[EmailChangeRequestResult]):
    """Request a verification code to change a user's email address.

    Verifies the new email is syntactically valid, then refreshes and
    dispatches a one-time code to it. The user instance is supplied by
    the view (already authenticated).

    No ownership check is performed here: revealing whether an address
    is already linked to an account would enable enumeration. Instead,
    the code is issued unconditionally, and ownership is decided at
    confirmation time — a caller who cannot present the code cannot
    complete the change, regardless of what the request step returned.

    Blocked contacts are treated the same way: a generic success
    response is returned, without revealing that the address exists but
    is blocked.

    The code is issued with ``purpose=CodePurpose.CHANGE_EMAIL``, so it
    cannot be replayed for a different operation (e.g. removing the
    same email).
    """

    def execute(self, *, user: User, new_email: str) -> EmailChangeRequestResult:
        """Request a code to change the user's email to ``new_email``.

        Args:
            user (User): The authenticated user requesting the change.
                Unused beyond authentication; kept for interface
                symmetry with the confirmation step.
            new_email (str): The email address that should replace the
                current one. Must be syntactically valid.

        Returns:
            EmailChangeRequestResult: The destination email and the
            code's expiry timestamp.

        Raises:
            ValidationError: If ``new_email`` is not a syntactically
                valid email address.
            BusinessError: If a still-valid code is already outstanding
                for this address.
        """
        if not is_valid_email(identifier=new_email):
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid email address"))
            )

        contact, _ = Email.objects.get_or_create(address=new_email)

        if contact.is_blocked:
            # Do not disclose that the contact exists but is blocked.
            # Return a success-shaped result that matches the real
            # path's shape, so the response cannot be used to probe
            # block state.
            return self._generic_result(new_email)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_change_email_code()
        self._dispatch(contact, verification_code=verification_code)

        return EmailChangeRequestResult(
            new_email=new_email,
            expires_at=contact.code_expires_at,
        )

    def _generic_result(self, new_email: str) -> EmailChangeRequestResult:
        """Return a success-shaped result that discloses nothing.

        Used when the contact exists but is blocked, so the response is
        indistinguishable from the real success path — same
        ``new_email`` and a plausible ``expires_at`` computed from the
        default code TTL. No field reveals whether the address exists
        or is blocked.

        Args:
            new_email (str): The email address supplied by the caller.

        Returns:
            EmailChangeRequestResult: A result whose ``new_email``
            echoes the caller's input and whose ``expires_at`` is the
            current time plus the default code TTL — the same value the
            real path would produce.
        """
        return EmailChangeRequestResult(
            new_email=new_email,
            expires_at=timezone.now() + timedelta(minutes=DEFAULT_CODE_TTL_MINUTES),
        )

    def _dispatch(self, contact: Email, *, verification_code: str) -> None:
        """Send the verification code to ``contact``'s address.

        TODO: implement actual email delivery.

        Args:
            contact (Email): The contact record whose address should
                receive the code.
            verification_code (str): The six-digit code to deliver.
        """
        ...
