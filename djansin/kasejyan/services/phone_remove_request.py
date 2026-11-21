"""Service layer for requesting a phone-removal verification code.

Verifies that the target phone belongs to the authenticated user, then
dispatches a fresh one-time code to that phone. This is the first step
of the two-step phone-removal flow; the second step is handled by
:class:`RemovePhoneService`, which is where the "last login method"
guard is enforced.

Blocked phones are **not** rejected here: the caller has already proven
ownership by being authenticated, and removing a blocked phone is a
legitimate cleanup operation. The block state is reported explicitly by
:class:`RemovePhoneService` at confirmation time, after the code has
been verified.

The code is issued with ``purpose=CodePurpose.REMOVE_PHONE``, so it
cannot be replayed for a different operation (e.g. changing the same
phone number).

Ownership failures collapse into a single generic error, matching the
confirmation step's behavior, so this endpoint cannot be used to
enumerate phones or probe ownership.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import OperationNotAllowed
from core.services import Service
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Phone, User
from djansin.kasejyan.types import PhoneRemovalRequestResult


class RequestRemovePhoneService(Service[PhoneRemovalRequestResult]):
    """Request a verification code to remove a phone from a user's account.

    Verifies that the phone belongs to the user and that no still-valid
    code is already outstanding, then refreshes the code on the phone
    and dispatches it. The user instance is supplied by the view
    (already authenticated).

    Blocked phones are **not** rejected here: the caller has already
    proven ownership by being authenticated, and removing a blocked
    phone is a legitimate cleanup operation. The block state is
    reported explicitly by :class:`RemovePhoneService` at confirmation
    time, after the code has been verified.

    This step does **not** decide whether the removal itself is
    permitted — that decision is made by :class:`RemovePhoneService` at
    confirmation time, once the caller has proven access to the phone
    by presenting the code.

    Ownership failures collapse into a single generic error, matching
    the confirmation step's behavior, so this endpoint cannot be used
    to enumerate phones or probe ownership.
    """

    def execute(self, *, user: User, phone: str) -> PhoneRemovalRequestResult:
        """Request a code to remove ``phone`` from ``user``'s account.

        Args:
            user (User): The authenticated user requesting the removal.
            phone (str): The phone number to detach. Must belong to
                ``user``. May be currently blocked — blocked phones can
                still be removed.

        Returns:
            PhoneRemovalRequestResult: The destination phone and the
            code's expiry timestamp.

        Raises:
            BusinessError: If the phone does not belong to the user or
                a still-valid code is already outstanding.
        """
        contact = self._resolve_contact(user=user, phone=phone)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_remove_phone_code()
        self._dispatch(contact, verification_code=verification_code)

        return PhoneRemovalRequestResult(
            phone=phone,
            expires_at=contact.code_expires_at,
        )

    def _resolve_contact(self, *, user: User, phone: str) -> Phone:
        """Resolve the phone row owned by ``user``.

        Deliberately does not distinguish "does not exist" from
        "belongs to another user", to avoid leaking phone ownership
        across users. Both cases collapse into the same generic error
        used by the confirmation step.

        A blocked phone is still resolved — blocking does not prevent
        removal.

        Args:
            user (User): The authenticated user.
            phone (str): The phone number to resolve.

        Returns:
            Phone: The matching contact record.

        Raises:
            BusinessError: If no row exists for ``phone`` owned by
                ``user``.
        """
        contact = (
            Phone.objects.filter(number=phone, user=user).select_related("user").first()
        )

        if contact is None:
            raise BusinessError(
                OperationNotAllowed(
                    reason=_t("The provided phone number is not owned by the user.")
                )
            )

        return contact

    def _dispatch(self, contact: Phone, *, verification_code: str) -> None:
        """Send the verification code to ``contact``'s number.

        TODO: implement actual SMS delivery.

        Args:
            contact (Phone): The contact record whose number should
                receive the code.
            verification_code (str): The six-digit code to deliver.
        """
        ...
