"""Model definition for the :class:`Email` contact entity.

This module defines :class:`Email`, a concrete model representing a unique
email address that may be linked one-to-one with a user account. The model
combines :class:`~djansin.kasejyan.models.mixins.verifiable.VerifiableMixin`
(for one-time verification code behavior) with
:class:`~core.models.base.Model` (for shared identity and timestamp
fields), and is managed by
:class:`~djansin.kasejyan.models.managers.email.EmailManager`.
"""

from django.conf import settings
from django.core.validators import EmailValidator
from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.models.base import Model
from djansin.kasejyan.models.managers.email import EmailManager
from djansin.kasejyan.models.mixins.verifiable import VerifiableMixin


class Email(VerifiableMixin, Model):
    """Concrete model representing a unique, verifiable email address.

    Encapsulates a single email address that can optionally be attached to
    a user account via a one-to-one relation. The associated
    :class:`VerifiableMixin` supplies the fields and helpers required to
    issue, expire, and validate one-time verification codes for this
    address.

    Attributes:
        objects (EmailManager): Default manager bound to
            :class:`~djansin.kasejyan.models.managers.email.EmailManager`.
        user (User | None): Optional one-to-one link to the owning user
            account. Set to ``None`` when the user is deleted.
        address (str): The unique email address, validated by
            :class:`~django.core.validators.EmailValidator` and capped at
            254 characters.
    """

    objects: EmailManager = EmailManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="email",
        verbose_name=_t("User"),
        help_text=_t("The user account associated with this email address."),
    )

    address = models.EmailField(
        unique=True,
        max_length=254,
        validators=[
            EmailValidator(
                message=_t("Enter a valid email address (e.g., name@example.com)")
            )
        ],
        verbose_name=_t("Email Address"),
        help_text=_t("Example: user@domain.com - Maximum 254 characters"),
        error_messages={"unique": _t("This email address is already registered.")},
    )

    def __str__(self) -> str:
        return self.address
