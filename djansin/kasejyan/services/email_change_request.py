"""Service layer for requesting an email-change verification code.

Verifies that the target email is not already linked to the user (or
anyone else), then dispatches a fresh one-time code to it. This is the
first step of the two-step email-change flow; the second step is
handled by :class:`ChangeEmailService`.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import BusinessRuleViolation
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils.user_identifier import is_valid_email
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.types import EmailChangeRequestResult


class RequestChangeEmailService(Service[EmailChangeRequestResult]):
    """Request a verification code to change a user's email address.

    Verifies the new email is not already linked to the user or anyone
    else, then refreshes and dispatches a one-time code to it. The user
    instance is supplied by the view (already authenticated).
    """

    def execute(self, *, user: User, new_email: str) -> EmailChangeRequestResult:
        if not is_valid_email(identifier=new_email):
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid email address"))
            )

        contact, _ = Email.objects.get_or_create(address=new_email)

        if not contact.is_expired:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "A verification code has already been sent and is still valid. Please wait before requesting a new one."
                    )
                )
            )

        verification_code = contact.refresh_code()
        self._dispatch(email=new_email, verification_code=verification_code)

        return EmailChangeRequestResult(
            new_email=new_email,
            expires_at=contact.code_expires_at,
        )

    def _dispatch(self, *, email: str, verification_code: str) -> None:
        """Send the verification code to ``email``.

        TODO: implement actual email delivery.
        """
        ...
