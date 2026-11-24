"""Service layer for verifying one-time contact codes.

Exposes :class:`VerifyContactService`, which validates a purpose-scoped
one-time code against a contact record (``Email`` or ``Phone``),
consuming an attempt on mismatch and marking the contact as verified on
success. All failures collapse into a single generic error to avoid
leaking whether the contact exists, is blocked, the code expired, or
the code was issued for a different purpose.

Blocked contacts are rejected before any code check, so a temporarily
blocked contact cannot be verified (and therefore cannot be used to
authorize an operation) until the block expires.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import DomainError
from core.services import Service
from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.exceptions import InvalidVerificationCode
from djansin.kasejyan.models import Email, Phone
from djansin.kasejyan.types import VerifiedContactResult


class VerifyContactService(Service[VerifiedContactResult]):
    """Verify a purpose-scoped one-time code sent to a contact.

    Resolves the contact, checks that it is not temporarily blocked,
    checks that the current code was issued for ``purpose``, then checks
    expiry, attempt limits, and the code value itself. On success, the
    code is invalidated and the contact is marked as verified. Returns a
    :class:`VerifiedContactResult` describing the verified contact and,
    if linked, its user.

    Purpose is checked **before** the code value, so a code issued for
    one operation cannot be replayed for another (e.g. a "change email"
    code cannot authorize an "remove email" operation), even if the
    digits happen to match. A wrong-purpose attempt does not consume an
    attempt, since the caller simply presented a code for a different
    operation.

    Every rejection is raised as a :class:`~core.exceptions.DomainError`
    wrapping :class:`~djansin.kasejyan.exceptions.InvalidVerificationCode`
    — a single, generic domain error regardless of the underlying cause
    (missing contact, blocked contact, wrong purpose, expired code,
    exhausted attempts, mismatched value). This prevents the endpoint
    from acting as an oracle for contact existence, block state, code
    state, or purpose.
    """

    def execute(
        self, identifier: str, code: str, *, purpose: str
    ) -> VerifiedContactResult:
        """Verify ``code`` for ``purpose`` against ``identifier``.

        Args:
            identifier (str): The email address or phone number that
                received the code.
            code (str): The six-digit verification code to check.
            purpose (str): The :class:`CodePurpose` value the code must
                have been issued for. Required — callers must be
                explicit about which operation they are authorizing.

        Returns:
            VerifiedContactResult: Describes the verified contact,
            including its user (if linked) and whether this call was
            the one that transitioned it to verified.

        Raises:
            DomainError: When the identifier is not a valid contact,
                the contact does not exist, the contact is temporarily
                blocked, the code was issued for a different purpose,
                the code is expired, the attempt limit has been
                reached, or the code does not match. All cases collapse
                into the same generic
                :class:`~djansin.kasejyan.exceptions.InvalidVerificationCode`.
        """
        contact, contact_type = self._resolve_contact(identifier)

        self._ensure_not_blocked(contact, contact_type=contact_type)
        self._ensure_purpose_matches(
            contact, purpose=purpose, contact_type=contact_type
        )
        self._ensure_verifiable(contact, contact_type=contact_type)
        self._ensure_code_matches(contact, code=code, contact_type=contact_type)

        was_verified = contact.is_verified

        contact.invalidate()
        if not was_verified:
            contact.verify()

        return VerifiedContactResult(
            contact_type=contact.get_model_name(),
            identifier=str(contact),
            user=contact.user,
            is_newly_verified=not was_verified,
        )

    def _resolve_contact(self, identifier: str) -> tuple[Email | Phone, str]:
        """Resolve the contact record and its human-readable type.

        Args:
            identifier (str): The email address or phone number.

        Returns:
            tuple[Email | Phone, str]: The contact record and a
            human-readable label (``"email address"`` or
            ``"phone number"``) used in error messages.

        Raises:
            DomainError: When ``identifier`` is neither a valid email
                nor a valid phone number, or no contact record exists.
                Both cases collapse into the same generic error.
        """
        if is_valid_email(identifier):
            contact = Email.objects.find_by_address(address=identifier)
            contact_type = _t("email address")
        elif is_valid_phone(identifier):
            contact = Phone.objects.find_by_number(number=identifier)
            contact_type = _t("phone number")
        else:
            raise DomainError(InvalidVerificationCode(target=_t("identifier")))

        if contact is None:
            raise DomainError(InvalidVerificationCode(target=contact_type))

        return contact, contact_type

    def _ensure_not_blocked(self, contact: Email | Phone, *, contact_type: str) -> None:
        """Reject contacts that are temporarily blocked.

        A contact is considered blocked when ``blocked_until`` is set and
        lies in the future. Blocking is used to throttle repeated failed
        attempts or to honour a security policy; a blocked contact must
        not be verifiable until the block expires.

        This check runs **before** purpose, expiry, attempt, and value
        checks, so a blocked contact never reveals anything about its
        code state — every probe yields the same generic error.

        Args:
            contact (Email | Phone): The contact record.
            contact_type (str): Human-readable contact label for the
                error message.

        Raises:
            DomainError: If the contact is currently blocked.
        """
        if contact.is_blocked:
            raise DomainError(InvalidVerificationCode(target=contact_type))

    def _ensure_purpose_matches(
        self, contact: Email | Phone, *, purpose: str, contact_type: str
    ) -> None:
        """Reject the code if it was issued for a different purpose.

        This check runs **before** expiry, attempt-limit, and value
        checks. A wrong-purpose attempt does not consume an attempt:
        the caller presented a code for a different operation, and
        nothing about the target operation's code state is learned.

        Args:
            contact (Email | Phone): The contact record.
            purpose (str): The expected :class:`CodePurpose` value.
            contact_type (str): Human-readable contact label for the
                error message.

        Raises:
            DomainError: If the contact's current code was not issued
                for ``purpose``.
        """
        if not contact.matches_purpose(purpose):
            raise DomainError(InvalidVerificationCode(target=contact_type))

    def _ensure_verifiable(self, contact: Email | Phone, *, contact_type: str) -> None:
        """Reject expired contacts and those that hit the attempt limit.

        Args:
            contact (Email | Phone): The contact record.
            contact_type (str): Human-readable contact label for the
                error message.

        Raises:
            DomainError: If the code has expired or the maximum number
                of failed attempts has been reached.
        """
        if contact.is_expired:
            raise DomainError(InvalidVerificationCode(target=contact_type))

        if contact.max_attempts_reached:
            raise DomainError(InvalidVerificationCode(target=contact_type))

    def _ensure_code_matches(
        self, contact: Email | Phone, *, code: str, contact_type: str
    ) -> None:
        """Compare the supplied code; count a failed attempt on mismatch.

        Args:
            contact (Email | Phone): The contact record.
            code (str): The six-digit code supplied by the caller.
            contact_type (str): Human-readable contact label for the
                error message.

        Raises:
            DomainError: If the supplied code does not match the stored
                one. A failed attempt is recorded before raising, so
                repeated wrong guesses progressively lock the code out.
        """
        if contact.verification_code != code:
            contact.increment_attempts()
            raise DomainError(InvalidVerificationCode(target=contact_type))
