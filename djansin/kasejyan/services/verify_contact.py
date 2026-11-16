from django.utils.translation import gettext_lazy as _t

from core.exceptions import ValidationError
from core.services import Service
from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.exceptions import InvalidVerificationCode
from djansin.kasejyan.models import Email, Phone
from djansin.kasejyan.types import VerifiedContactResult


class VerifyContactService(Service[VerifiedContactResult]):
    """Verify a one-time code sent to an email address or phone number.

    Resolves the contact, checks the code against expiry, attempt
    limits, and value, then invalidates the code and marks the contact
    as verified. Returns a :class:`VerifiedContactResult` describing
    the verified contact and, if linked, its user.
    """

    def execute(self, identifier: str, code: str) -> VerifiedContactResult:
        """Verify the code for ``identifier``.

        Args:
            identifier (str): The email address or phone number that
                received the code.
            code (str): The one-time verification code to check.

        Returns:
            VerifiedContactResult: Describes the verified contact.

        Raises:
            ValidationError: When the identifier is not a valid contact,
                the contact does not exist, the code is expired, the
                attempt limit has been reached, or the code does not
                match.
        """
        contact, contact_type = self._resolve_contact(identifier)

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

        Raises:
            ValidationError: When ``identifier`` is neither a valid email
                nor a valid phone number, or no contact record exists.
        """
        if is_valid_email(identifier):
            contact = Email.objects.filter(address=identifier).first()
            contact_type = _t("email address")
        elif is_valid_phone(identifier):
            contact = Phone.objects.filter(number=identifier).first()
            contact_type = _t("phone number")
        else:
            raise ValidationError(InvalidVerificationCode(target=_t("identifier")))

        if contact is None:
            raise ValidationError(InvalidVerificationCode(target=contact_type))

        return contact, contact_type

    def _ensure_verifiable(self, contact: Email | Phone, *, contact_type: str) -> None:
        """Reject expired contacts and those that hit the attempt limit."""
        if contact.is_expired:
            raise ValidationError(InvalidVerificationCode(target=contact_type))

        if contact.max_attempts_reached:
            raise ValidationError(InvalidVerificationCode(target=contact_type))

    def _ensure_code_matches(
        self, contact: Email | Phone, *, code: str, contact_type: str
    ) -> None:
        """Compare the supplied code; count a failed attempt on mismatch."""
        if contact.verification_code != code:
            contact.increment_attempts()
            raise ValidationError(InvalidVerificationCode(target=contact_type))
