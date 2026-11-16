"""Service layer for requesting a password-reset verification code.

Resolves the user's preferred contact channel (phone first, then
email), generates a fresh verification code on that contact, and
dispatches it. Fails with a domain error when the user has no
contact channel at all.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.services import Service
from core.utils.user_identifier import is_valid_email
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.types import PasswordResetRequestResult


class RequestPasswordResetService(
    UserResolverMixin, Service[PasswordResetRequestResult]
):
    """Request a verification code to reset a user's password.

    Resolves the user from an email, phone number, or username, picks
    the first available contact channel (phone, then email), refreshes
    the code on that contact, and dispatches it. If the user has no
    contact channel, a domain error is raised — there is no way to
    verify ownership, so the reset cannot proceed.
    """

    def execute(self, identifier: str) -> PasswordResetRequestResult:
        user = self._resolve_user(identifier)

        if user is None:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        contact = self._pick_contact(user, identifier)

        if contact is None:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "User has no phone number or email address to receive the verification code."
                    )
                )
            )

        if not contact.is_expired:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "A verification code has already been sent and is still valid. Please wait before requesting a new one."
                    )
                )
            )

        verification_code = contact.refresh_code()
        self._dispatch(contact, verification_code=verification_code)

        return PasswordResetRequestResult(
            channel=contact.get_model_name(),
            identifier=str(contact),
            expires_at=contact.code_expires_at,
        )

    def _pick_contact(self, user: User, identifier: str) -> Email | Phone | None:
        """Return the user's preferred contact channel.

        Phone takes precedence over email. Returns ``None`` if the user
        has neither.
        """
        phone = getattr(user, "phone", None)
        email = getattr(user, "email", None)

        return email if is_valid_email(identifier) or phone is None else phone

    def _dispatch(self, contact: Email | Phone, *, verification_code: str) -> None:
        """Send the verification code through the contact's channel.

        TODO: implement actual SMS / email delivery.
        """
        ...
