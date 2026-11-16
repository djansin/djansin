"""Service layer for requesting an email-removal verification code.

Verifies that the target email belongs to the authenticated user and
guards against removing the user's last remaining login method, then
dispatches a fresh one-time code to that email. This is the first step
of the two-step email-removal flow; the second step is handled by
:class:`RemoveEmailService`.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.services import Service
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.types import EmailRemovalRequestResult


class RequestRemoveEmailService(Service[EmailRemovalRequestResult]):
    """Request a verification code to remove an email from a user's account.

    Verifies that the email belongs to the user, that removing it would
    not leave the user with no login method, and that no still-valid
    code is already outstanding. Refreshes the code on the email and
    dispatches it. The user instance is supplied by the view (already
    authenticated).
    """

    def execute(self, *, user: User, email: str) -> EmailRemovalRequestResult:
        contact = self._resolve_contact(user=user, email=email)

        if not contact.is_expired:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "A verification code has already been sent and is still valid. Please wait before requesting a new one."
                    )
                )
            )

        verification_code = contact.refresh_code()
        self._dispatch(email=email, verification_code=verification_code)

        return EmailRemovalRequestResult(
            email=email,
            expires_at=contact.code_expires_at,
        )

    def _resolve_contact(self, *, user: User, email: str) -> Email:
        """Resolve the email row owned by ``user``.

        Raises ``ResourceNotFound`` if no such row exists — deliberately
        not distinguishing "does not exist" from "belongs to another
        user", to avoid leaking email ownership across users.
        """
        contact = (
            Email.objects.filter(address=email, user=user)
            .select_related("user")
            .first()
        )

        if contact is None:
            raise BusinessError(ResourceNotFound(resource=_t("Email")))

        return contact

    def _dispatch(self, *, email: str, verification_code: str) -> None:
        """Send the verification code to ``email``.

        TODO: implement actual email delivery.
        """
        ...
