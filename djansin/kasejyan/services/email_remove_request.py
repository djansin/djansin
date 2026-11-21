"""Service layer for requesting an email-removal verification code.

Verifies that the target email belongs to the authenticated user, then
dispatches a fresh one-time code to that email. This is the first step
of the two-step email-removal flow; the second step is handled by
:class:`RemoveEmailService`, which is where the "last login method"
guard is enforced.

Blocked emails are **not** rejected here: the caller has already proven
ownership by being authenticated, and removing a blocked email is a
legitimate cleanup operation. The block state is reported explicitly
by :class:`RemoveEmailService` at confirmation time, after the code has
been verified.

The code is issued with ``purpose=CodePurpose.REMOVE_EMAIL``, so it
cannot be replayed for a different operation (e.g. changing the email).

Ownership failures collapse into a single generic error, matching the
confirmation step's behavior, so this endpoint cannot be used to
enumerate emails or probe ownership.
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import OperationNotAllowed
from core.services import Service
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Email, User
from djansin.kasejyan.types import EmailRemovalRequestResult


class RequestRemoveEmailService(Service[EmailRemovalRequestResult]):
    """Request a verification code to remove an email from a user's account.

    Verifies that the email belongs to the user and that no still-valid
    code is already outstanding, then refreshes the code on the email
    and dispatches it. The user instance is supplied by the view
    (already authenticated).

    Blocked emails are **not** rejected here: the caller has already
    proven ownership by being authenticated, and removing a blocked
    email is a legitimate cleanup operation. The block state is
    reported explicitly by :class:`RemoveEmailService` at confirmation
    time, after the code has been verified.

    This step does **not** decide whether the removal itself is
    permitted — that decision is made by :class:`RemoveEmailService` at
    confirmation time, once the caller has proven access to the email
    by presenting the code.

    Ownership failures collapse into a single generic error, matching
    the confirmation step's behavior, so this endpoint cannot be used
    to enumerate emails or probe ownership.
    """

    def execute(self, *, user: User, email: str) -> EmailRemovalRequestResult:
        """Request a code to remove ``email`` from ``user``'s account.

        Args:
            user (User): The authenticated user requesting the removal.
            email (str): The email address to detach. Must belong to
                ``user``. May be currently blocked — blocked emails can
                still be removed.

        Returns:
            EmailRemovalRequestResult: The destination email and the
            code's expiry timestamp.

        Raises:
            BusinessError: If the email does not belong to the user or
                a still-valid code is already outstanding.
        """
        contact = self._resolve_contact(user=user, email=email)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=email))

        verification_code = contact.refresh_remove_email_code()
        self._dispatch(email=email, verification_code=verification_code)

        return EmailRemovalRequestResult(
            email=email,
            expires_at=contact.code_expires_at,
        )

    def _resolve_contact(self, *, user: User, email: str) -> Email:
        """Resolve the email row owned by ``user``.

        Deliberately does not distinguish "does not exist" from
        "belongs to another user", to avoid leaking email ownership
        across users. Both cases collapse into the same generic error
        used by the confirmation step.

        Uses :meth:`EmailManager.find_by_address` scoped to the user,
        so a blocked email is still resolved — blocking does not
        prevent removal.

        Args:
            user (User): The authenticated user.
            email (str): The email address to resolve.

        Returns:
            Email: The matching contact record.

        Raises:
            BusinessError: If no row exists for ``email`` owned by
                ``user``.
        """
        contact = (
            Email.objects.filter(address=email, user=user)
            .select_related("user")
            .first()
        )

        if contact is None:
            raise BusinessError(
                OperationNotAllowed(
                    reason=_t("The provided email is not owned by the user.")
                )
            )

        return contact

    def _dispatch(self, *, email: str, verification_code: str) -> None:
        """Send the verification code to ``email``.

        TODO: implement actual email delivery.

        Args:
            email (str): The destination email address.
            verification_code (str): The six-digit code to deliver.
        """
        ...
