from core.exceptions import DomainError
from core.exceptions.errors.validation import VerificationCodeStillValid
from core.services import Service
from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.models import Email, Phone
from djansin.kasejyan.types import CodeDispatchResult


class VerificationCodeService(Service[CodeDispatchResult]):
    def execute(self, identifier: str) -> CodeDispatchResult:
        """Generate and dispatch a verification code for the identifier.

        Resolves (or lazily creates) the contact record matching
        ``identifier``, and, if the current code is expired, refreshes it
        and dispatches the new code through the appropriate channel
        (email or phone). If the code is still valid, no message is sent.

        Args:
            identifier (str): A valid email address or phone number to
                which the verification code should be sent.
        """
        contact = None
        if is_valid_email(identifier=identifier):
            contact: Email
            contact, _ = Email.objects.get_or_create(address=identifier)
        elif is_valid_phone(identifier=identifier):
            contact: Phone
            contact, _ = Phone.objects.get_or_create(number=identifier)

        if not contact.is_expired:
            raise DomainError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_code()
        self._dispatch(contact, verification_code=verification_code)
        return CodeDispatchResult(
            type=contact.get_model_name(),
            identifier=str(contact),
        )

    def _dispatch(self, contact: Email | Phone, *, verification_code: str) -> None:
        """Send the verification code through the contact's channel.

        TODO: implement actual SMS / email delivery.
        """
        ...
