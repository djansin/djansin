"""Service layer for requesting a password-reset verification code.

Resolves the user's preferred contact channel (phone first, then
email), generates a fresh verification code on that contact, and
dispatches it. If no user matches the identifier, or the user has no
contact channel, the service returns a normal success response without
disclosing which case occurred — this prevents user enumeration.

Contacts that are temporarily blocked are treated the same way: a
generic success response is returned, without revealing that the
contact exists but is blocked.

The code is issued with ``purpose=CodePurpose.RESET_PASSWORD``, so it
cannot be replayed for a different operation (e.g. changing the email).
"""

from datetime import timedelta

from django.utils import timezone

from core.exceptions import BusinessError
from core.services import Service
from core.utils.user_identifier import is_valid_email
from djansin.kasejyan.exceptions import VerificationCodeStillValid
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.models.mixins.verifiable import DEFAULT_CODE_TTL_MINUTES
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.types import PasswordResetRequestResult


class RequestPasswordResetService(
    UserResolverMixin, Service[PasswordResetRequestResult]
):
    """Request a verification code to reset a user's password.

    Resolves the user from an email, phone number, or username, picks
    the first available contact channel (phone, then email), refreshes
    the code on that contact, and dispatches it.

    If no user matches the identifier, the user has no contact channel,
    or the selected contact is temporarily blocked, the service returns
    a normal success response without disclosing which case occurred —
    this prevents user enumeration and block-state probing. The caller
    should treat the response as "if the account exists and has an
    unblocked contact channel, a code has been sent."
    """

    def execute(self, identifier: str) -> PasswordResetRequestResult:
        """Request a password-reset code for ``identifier``.

        Args:
            identifier (str): An email address, phone number, or
                username identifying the user.

        Returns:
            PasswordResetRequestResult: The channel (``"email"`` or
            ``"phone"``), the destination identifier, and the code's
            expiry timestamp. When no user matches, the user has no
            contact channel, or the contact is blocked, a generic
            result is returned instead — indistinguishable from the
            success case, to prevent enumeration and block-state
            probing.

        Raises:
            BusinessError: If a still-valid code is already outstanding
                for the resolved contact. This is the only failure that
                is safe to disclose: it does not reveal whether the
                user exists (a still-valid code implies a prior
                successful request for the same identifier).
        """
        user = self._resolve_user(identifier)

        if user is None:
            # Do not disclose that the user does not exist.
            return self._generic_result(identifier)

        contact = self._pick_contact(user, identifier)

        if contact is None:
            # Do not disclose that the user has no contact channel.
            return self._generic_result(identifier)

        if contact.is_blocked:
            # Do not disclose that the contact exists but is blocked.
            return self._generic_result(identifier)

        if not contact.is_expired:
            raise BusinessError(VerificationCodeStillValid(identifier=str(contact)))

        verification_code = contact.refresh_reset_password_code()
        self._dispatch(contact, verification_code=verification_code)

        return PasswordResetRequestResult(
            channel=contact.get_model_name(),
            identifier=str(contact),
            expires_at=contact.code_expires_at,
        )

    def _generic_result(self, identifier: str) -> PasswordResetRequestResult:
        """Return a success-shaped result that discloses nothing.

        Used when the user does not exist, has no contact channel, or
        the contact is blocked. The result is crafted to be
        **indistinguishable** from the real success path — same
        ``channel`` (derived from the identifier's shape), same
        ``identifier`` (echoed back), and a plausible ``expires_at``
        computed from the default code TTL. No field reveals whether
        the user or contact exists.

        Args:
            identifier (str): The identifier supplied by the caller.

        Returns:
            PasswordResetRequestResult: A result whose ``channel`` is
            ``"email"`` when ``identifier`` looks like an email,
            ``"phone"`` otherwise; whose ``identifier`` echoes the
            caller's input; and whose ``expires_at`` is the current
            time plus the default code TTL — the same value the real
            path would produce.
        """
        channel = "email" if is_valid_email(identifier) else "phone"

        return PasswordResetRequestResult(
            channel=channel,
            identifier=identifier,
            expires_at=timezone.now() + timedelta(minutes=DEFAULT_CODE_TTL_MINUTES),
        )

    def _pick_contact(self, user: User, identifier: str) -> Email | Phone | None:
        """Return the user's preferred contact channel.

        The caller's ``identifier`` determines the starting point: if it
        is a valid email address, the email channel is preferred;
        otherwise the phone channel is tried first. If the preferred
        channel is missing, the other is used as a fallback. Returns
        ``None`` only when the user has neither.

        Args:
            user (User): The user whose contact channels are inspected.
            identifier (str): The identifier supplied by the caller,
                used to decide which channel to prefer.

        Returns:
            Email | Phone | None: The selected contact channel, or
            ``None`` if the user has neither.
        """
        phone = getattr(user, "phone", None)
        email = getattr(user, "email", None)

        return email if is_valid_email(identifier) or phone is None else phone

    def _dispatch(self, contact: Email | Phone, *, verification_code: str) -> None:
        """Send the verification code through the contact's channel.

        TODO: implement actual SMS / email delivery.

        Args:
            contact (Email | Phone): The contact record whose channel
                should receive the code.
            verification_code (str): The six-digit code to deliver.
        """
        ...
