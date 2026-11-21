"""Service layer for requesting a one-time verification code.

Exposes :class:`VerificationCodeService`, which resolves (or lazily
creates) the contact record for a given identifier, refreshes its code
if the current one has expired, and dispatches the new code through the
appropriate channel (email or phone). Used by the passwordless
sign-in/sign-up flow.

Contacts that are temporarily blocked are rejected before a new code is
issued, so a blocked contact cannot be used to trigger repeated
dispatches. The issued code is purpose-scoped to ``AUTHENTICATE`` and
cannot authorize any other operation.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Email, Phone
from djansin.kasejyan.types import CodeDispatchResult


class VerificationCodeService(Service[CodeDispatchResult]):
    """Generate and dispatch a verification code for a contact.

    Resolves (or lazily creates) the contact record matching
    ``identifier``, rejects it if it is temporarily blocked, and, if the
    current code is expired, refreshes it and dispatches the new code
    through the appropriate channel (email or phone). If the current
    code is still valid, no message is sent and a
    :class:`~djansin.kasejyan.exceptions.VerificationCodeStillValid`
    error is raised.

    The code is issued with ``purpose=CodePurpose.AUTHENTICATE``, so it
    can only be used to complete a passwordless sign-in — not to
    authorize any other operation.
    """

    def execute(self, identifier: str) -> CodeDispatchResult:
        """Generate and dispatch a verification code for ``identifier``.

        Args:
            identifier (str): A valid email address or phone number to
                which the verification code should be sent.

        Returns:
            CodeDispatchResult: The contact type (``"email"`` or
            ``"phone"``) and the destination identifier.

        Raises:
            ValidationError: If ``identifier`` is neither a valid email
                address nor a valid phone number.
            BusinessError: If the contact is temporarily blocked, or a
                still-valid code is already outstanding for it.
        """
        if is_valid_email(identifier=identifier):
            contact, _ = Email.objects.get_or_create(address=identifier)
        elif is_valid_phone(identifier=identifier):
            contact, _ = Phone.objects.get_or_create(number=identifier)
        else:
            raise ValidationError(
                InvalidFormat(
                    expected_format=_t("a valid email address or phone number")
                )
            )

        self._ensure_not_blocked(contact)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_authenticate_code()
        self._dispatch(contact, verification_code=verification_code)

        return CodeDispatchResult(
            type=contact.get_model_name(),
            identifier=str(contact),
        )

    def _ensure_not_blocked(self, contact: Email | Phone) -> None:
        """Reject contacts that are temporarily blocked.

        A blocked contact must not be able to trigger a new code
        dispatch until the block expires — otherwise an attacker could
        keep the victim's phone or inbox flooded even after being
        throttled. This check runs after ``get_or_create`` so a
        freshly-created contact (which is never blocked) passes
        through, while an existing blocked one is rejected.

        Args:
            contact (Email | Phone): The contact record.

        Raises:
            BusinessError: If the contact is currently blocked.
        """
        if contact.blocked_until is not None and contact.blocked_until > timezone.now():
            raise BusinessError(
                BusinessRuleViolation(reason=_t("This contact is temporarily blocked."))
            )

    def _dispatch(self, contact: Email | Phone, *, verification_code: str) -> None:
        """Send the verification code through the contact's channel.

        TODO: implement actual SMS / email delivery.

        Args:
            contact (Email | Phone): The contact record whose channel
                should receive the code.
            verification_code (str): The six-digit code to deliver.
        """
        ...
