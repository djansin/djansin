"""Service layer for requesting a phone-change verification code.

Dispatches a fresh one-time code to the target phone without revealing
whether the number is already linked to any account. Ownership is
decided at confirmation time, once the caller has proven access to the
number by presenting the code. This is the first step of the two-step
phone-change flow; the second step is handled by
:class:`ChangePhoneService`.

Contacts that are temporarily blocked are treated like any other
number: a generic success response is returned, without revealing that
the number exists but is blocked.

The code is issued with ``purpose=CodePurpose.CHANGE_PHONE``, so it
cannot be replayed for a different operation (e.g. removing the same
phone number).
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils.user_identifier import is_valid_phone
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Phone, User
from djansin.kasejyan.models.mixins.verifiable import DEFAULT_CODE_TTL_MINUTES
from djansin.kasejyan.types import PhoneChangeRequestResult


class RequestChangePhoneService(Service[PhoneChangeRequestResult]):
    """Request a verification code to change a user's phone number.

    Verifies the new phone is syntactically valid, then refreshes and
    dispatches a one-time code to it. The user instance is supplied by
    the view (already authenticated).

    No ownership check is performed here: revealing whether a number is
    already linked to an account would enable enumeration. Instead, the
    code is issued unconditionally, and ownership is decided at
    confirmation time — a caller who cannot present the code cannot
    complete the change, regardless of what the request step returned.

    Blocked contacts are treated the same way: a generic success
    response is returned, without revealing that the number exists but
    is blocked.

    The code is issued with ``purpose=CodePurpose.CHANGE_PHONE``, so it
    cannot be replayed for a different operation (e.g. removing the
    same phone number).
    """

    def execute(self, *, user: User, new_phone: str) -> PhoneChangeRequestResult:
        """Request a code to change the user's phone to ``new_phone``.

        Args:
            user (User): The authenticated user requesting the change.
                Unused beyond authentication; kept for interface
                symmetry with the confirmation step.
            new_phone (str): The phone number that should replace the
                current one. Must be syntactically valid.

        Returns:
            PhoneChangeRequestResult: The destination phone and the
            code's expiry timestamp.

        Raises:
            ValidationError: If ``new_phone`` is not a syntactically
                valid phone number.
            BusinessError: If a still-valid code is already outstanding
                for this number.
        """
        if not is_valid_phone(identifier=new_phone):
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        contact, _ = Phone.objects.get_or_create(number=new_phone)

        if contact.is_blocked:
            # Do not disclose that the contact exists but is blocked.
            # Return a success-shaped result that matches the real
            # path's shape, so the response cannot be used to probe
            # block state.
            return self._generic_result(new_phone)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_change_phone_code()
        self._dispatch(contact, verification_code=verification_code)

        return PhoneChangeRequestResult(
            new_phone=new_phone,
            expires_at=contact.code_expires_at,
        )

    def _generic_result(self, new_phone: str) -> PhoneChangeRequestResult:
        """Return a success-shaped result that discloses nothing.

        Used when the contact exists but is blocked, so the response is
        indistinguishable from the real success path — same
        ``new_phone`` and a plausible ``expires_at`` computed from the
        default code TTL. No field reveals whether the number exists
        or is blocked.

        Args:
            new_phone (str): The phone number supplied by the caller.

        Returns:
            PhoneChangeRequestResult: A result whose ``new_phone``
            echoes the caller's input and whose ``expires_at`` is the
            current time plus the default code TTL — the same value the
            real path would produce.
        """
        return PhoneChangeRequestResult(
            new_phone=new_phone,
            expires_at=timezone.now() + timedelta(minutes=DEFAULT_CODE_TTL_MINUTES),
        )

    def _dispatch(self, contact: Phone, *, verification_code: str) -> None:
        """Send the verification code to ``contact``'s number.

        TODO: implement actual SMS delivery.

        Args:
            contact (Phone): The contact record whose number should
                receive the code.
            verification_code (str): The six-digit code to deliver.
        """
        ...
