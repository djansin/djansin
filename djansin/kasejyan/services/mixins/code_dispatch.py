"""Reusable mixin for dispatching one-time verification codes.

Defines :class:`CodeDispatchMixin`, which provides a single
:meth:`dispatch_code` entry point that routes a verification code to the
correct delivery channel based on the contact type (email or phone).
Concrete delivery is delegated to two overridable hooks,
:meth:`_send_email` and :meth:`_send_sms`, so the mixin can be reused
across services without coupling them to a specific transport.

Typical usage::

    class VerificationCodeService(CodeDispatchMixin, Service[CodeDispatchResult]):
        def execute(self, identifier: str) -> CodeDispatchResult:
            ...
            self.dispatch_code(contact, verification_code=code)
            ...
"""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import BusinessRuleViolation
from djansin.kasejyan.models import Email, Phone


class CodeDispatchMixin:
    """Mixin providing channel-aware delivery of verification codes.

    Routes a verification code to the correct transport (email or SMS)
    based on the concrete contact type. Subclasses override
    :meth:`_send_email` and :meth:`_send_sms` to plug in their actual
    delivery implementation (Django email backend, SMS gateway, etc.).

    The default implementations are no-ops that raise
    :class:`NotImplementedError` — subclasses must override at least the
    channels they use. This makes missing wiring fail loudly at the
    first call rather than silently dropping codes.
    """

    def dispatch_code(
        self,
        contact: Email | Phone,
        *,
        verification_code: str,
    ) -> None:
        """Deliver ``verification_code`` through the contact's channel.

        Selects the transport based on the contact type: :class:`Email`
        records are delivered via :meth:`_send_email`; :class:`Phone`
        records via :meth:`_send_sms`. Any other type is rejected with a
        business error, since the mixin only knows how to reach those
        two channels.

        Args:
            contact (Email | Phone): The contact record whose channel
                should receive the code.
            verification_code (str): The six-digit code to deliver.

        Raises:
            BusinessError: If ``contact`` is neither an :class:`Email`
                nor a :class:`Phone` instance.
            NotImplementedError: If the relevant channel hook has not
                been overridden by the subclass.
        """
        if isinstance(contact, Email):
            self._send_email(contact, verification_code=verification_code)
            return

        if isinstance(contact, Phone):
            self._send_sms(contact, verification_code=verification_code)
            return

        raise BusinessError(
            BusinessRuleViolation(
                reason=_t("Unsupported contact type for verification code delivery.")
            )
        )

    def _send_email(self, contact: Email, *, verification_code: str) -> None:
        """Deliver ``verification_code`` to ``contact`` via email.

        Override in subclasses to plug in the actual email backend.

        Args:
            contact (Email): The email contact record.
            verification_code (str): The six-digit code to deliver.

        Raises:
            NotImplementedError: Always, unless overridden.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement _send_email()."
        )

    def _send_sms(self, contact: Phone, *, verification_code: str) -> None:
        """Deliver ``verification_code`` to ``contact`` via SMS.

        Override in subclasses to plug in the actual SMS gateway.

        Args:
            contact (Phone): The phone contact record.
            verification_code (str): The six-digit code to deliver.

        Raises:
            NotImplementedError: Always, unless overridden.
        """
        raise NotImplementedError(f"{type(self).__name__} must implement _send_sms().")
