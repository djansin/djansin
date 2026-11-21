"""Model definition for the :class:`Phone` contact entity.

This module defines :class:`Phone`, a concrete model representing a unique
phone number that may be linked one-to-one with a user account. The model
combines :class:`~djansin.kasejyan.models.mixins.verifiable.VerifiableMixin`
(for one-time verification code behavior) with
:class:`~core.models.base.Model` (for shared identity and timestamp
fields), and is managed by
:class:`~djansin.kasejyan.models.managers.phone.PhoneManager`.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _t
from phonenumber_field.modelfields import PhoneNumberField

from core.models.base import Model
from core.models.mixins import BlockableMixin
from djansin.kasejyan.models.managers.phone import PhoneManager
from djansin.kasejyan.models.mixins.verifiable import (
    DEFAULT_CODE_TTL_MINUTES,
    VerifiableMixin,
)


class Phone(VerifiableMixin, BlockableMixin, Model):
    """Concrete model representing a unique, verifiable phone number.

    Encapsulates a single phone number that can optionally be attached to
    a user account via a one-to-one relation. The associated
    :class:`VerifiableMixin` supplies the fields and helpers required to
    issue, expire, and validate one-time verification codes for this
    number.

    Attributes:
        objects (PhoneManager): Default manager bound to
            :class:`~djansin.kasejyan.models.managers.phone.PhoneManager`.
        user (User | None): Optional one-to-one link to the owning user
            account. Set to ``None`` when the user is deleted.
        number (phonenumber_field.modelfields.PhoneNumberField): The unique
            phone number stored in international format with country code.
    """

    objects: PhoneManager = PhoneManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="phone",
        null=True,
        blank=True,
        verbose_name=_t("User"),
        help_text=_t("The user account associated with this phone number."),
    )

    number = PhoneNumberField(
        unique=True,
        verbose_name=_t("Phone Number"),
        help_text=_t("Enter phone number with country code (e.g., +989123456789)"),
        error_messages={"unique": _t("This phone number is already registered.")},
    )

    def refresh_change_phone_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing a phone change.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.CHANGE_CONTACT, minutes=minutes, save=save
        )

    def refresh_remove_phone_code(
        self,
        minutes: int = DEFAULT_CODE_TTL_MINUTES,
        save: bool = True,
    ) -> str:
        """Issue a code authorizing a phone removal.

        Args:
            minutes (int, optional): Time-to-live for the new code, in
                minutes. Defaults to :data:`DEFAULT_CODE_TTL_MINUTES`.
            save (bool, optional): Whether to persist the changes.

        Returns:
            str: The newly generated verification code.
        """
        return self.refresh_code(
            purpose=self.CodePurpose.REMOVE_CONTACT, minutes=minutes, save=save
        )

    def __str__(self) -> str:
        return self.number.as_e164
