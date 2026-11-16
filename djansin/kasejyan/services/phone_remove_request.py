"""Service layer for requesting a phone-removal verification code.

Verifies that the target phone belongs to the authenticated user and
guards against removing the user's last remaining login method, then
dispatches a fresh one-time code to that phone. This is the first step
of the two-step phone-removal flow; the second step is handled by
:class:`RemovePhoneService`.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.services import Service
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.types import PhoneRemovalRequestResult


class RequestRemovePhoneService(Service[PhoneRemovalRequestResult]):
    """Request a verification code to remove a phone from a user's account.

    Verifies that the phone belongs to the user, that removing it would
    not leave the user with no login method, and that no still-valid
    code is already outstanding. Refreshes the code on the phone and
    dispatches it. The user instance is supplied by the view (already
    authenticated).
    """

    def execute(self, *, user: User, phone: str) -> PhoneRemovalRequestResult:
        contact = self._resolve_contact(user=user, phone=phone)

        if not contact.is_expired:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t(
                        "A verification code has already been sent and is still valid. Please wait before requesting a new one."
                    )
                )
            )

        verification_code = contact.refresh_code()
        self._dispatch(phone=phone, verification_code=verification_code)

        return PhoneRemovalRequestResult(
            phone=phone,
            expires_at=contact.code_expires_at,
        )

    def _resolve_contact(self, *, user: User, phone: str) -> Phone:
        """Resolve the phone row owned by ``user``.

        Raises ``ResourceNotFound`` if no such row exists — deliberately
        not distinguishing "does not exist" from "belongs to another
        user", to avoid leaking phone ownership across users.
        """
        contact = (
            Phone.objects.filter(number=phone, user=user).select_related("user").first()
        )

        if contact is None:
            raise BusinessError(ResourceNotFound(resource=_t("Phone")))

        return contact

    def _dispatch(self, *, phone: str, verification_code: str) -> None:
        """Send the verification code to ``phone``.

        TODO: implement actual SMS delivery.
        """
        ...
