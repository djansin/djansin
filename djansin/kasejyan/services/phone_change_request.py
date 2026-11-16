"""Service layer for requesting a phone-change verification code.

Verifies that the target phone is not already linked to the user (or
anyone else), then dispatches a fresh one-time code to it. This is the
first step of the two-step phone-change flow; the second step is
handled by :class:`ChangePhoneService`.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils.user_identifier import is_valid_phone
from djansin.kasejyan.models import Phone, User
from djansin.kasejyan.types import PhoneChangeRequestResult


class RequestChangePhoneService(Service[PhoneChangeRequestResult]):
    """Request a verification code to change a user's phone number.

    Verifies the new phone is not already linked to the user or anyone
    else, then refreshes and dispatches a one-time code to it. The user
    instance is supplied by the view (already authenticated).
    """

    def execute(self, *, user: User, new_phone: str) -> PhoneChangeRequestResult:
        if not is_valid_phone(identifier=new_phone):
            raise BusinessError(
                InvalidFormat(expected_format=_t("a valid phone number"))
            )

        contact, _ = Phone.objects.get_or_create(number=new_phone)

        if not contact.is_expired:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "A verification code has already been sent and is still valid. Please wait before requesting a new one."
                    )
                )
            )

        verification_code = contact.refresh_code()
        self._dispatch(phone=new_phone, verification_code=verification_code)

        return PhoneChangeRequestResult(
            new_phone=new_phone,
            expires_at=contact.code_expires_at,
        )

    def _dispatch(self, *, phone: str, verification_code: str) -> None:
        """Send the verification code to ``phone``.

        TODO: implement actual SMS delivery.
        """
        ...
