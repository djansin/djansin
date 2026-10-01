"""Confirmable model mixin providing confirmation and interaction tracking.

This module defines an abstract model mixin that adds confirmation and
interaction tracking capabilities to Django models. The mixin allows records
to be confirmed (verified) and tracks the last successful interaction with
the record.

Common use cases include:
- Email verification for user accounts
- Phone number verification (OTP)
- Document verification workflows
- First-time login confirmation
- Any process requiring user confirmation or validation
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.exceptions.common import BusinessError
from core.exceptions.errors.business import (
    ResourceAlreadyConfirmed,
    ResourceNotConfirmed,
    ResourceNotSaved,
)
from core.models.mixins.abstract import AbstractModelMixin


class ConfirmableMixin(AbstractModelMixin):
    """An abstract model mixin that adds confirmation and interaction tracking.

    This mixin extends AbstractModelMixin with confirmation and interaction
    tracking capabilities. It provides two timestamp fields:
    - `confirmed_at`: Tracks when the record was initially confirmed
    - `last_confirmed_at`: Tracks the last successful interaction

    Key features:
    - Automatic timestamp tracking (created_at, updated_at) from AbstractModelMixin
    - Confirmation status checking via `is_confirmed` property
    - Age calculations for confirmation and interaction
    - Recent interaction checking
    - Confirmation with idempotency protection
    - Interaction updating for confirmed records

    The mixin follows the principle that interaction tracking should only
    occur for confirmed records, ensuring that unconfirmed records cannot
    have their interaction timestamps updated.

    Attributes:
        confirmed_at: A nullable DateTimeField storing when the record was
            confirmed. Null means the record is not confirmed.

        last_confirmed_at: A nullable DateTimeField storing the last
            successful interaction with the record. Null means the record
            has never had an interaction.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    # Confirmation status
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Confirmed At"),
        help_text=_t("Timestamp when the contact has been confirmed."),
    )

    # Last confirmed interaction
    last_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_t("Last Confirmed At"),
        help_text=_t(
            "Last successful interaction confirming ownership (login, OTP, or confirmed communication)."
        ),
    )

    class Meta:
        """Metadata configuration for ConfirmableMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides confirmation fields to all inheriting models.
        """

        abstract = True

    @property
    def is_confirmed(self) -> bool:
        """Check if the record has been confirmed.

        Returns:
            True if confirmed_at is set, False otherwise.
        """
        return self.confirmed_at is not None

    @property
    def confirmation_age_days(self) -> int | None:
        """Get the number of days since confirmation.

        Returns:
            The number of days since confirmation, or None if not confirmed.
        """
        if not self.confirmed_at:
            return None
        delta = timezone.now() - self.confirmed_at
        return delta.days

    @property
    def interaction_age_days(self) -> int | None:
        """Get the number of days since the last interaction.

        Returns:
            The number of days since the last interaction, or None if
            never interacted.
        """
        if not self.last_confirmed_at:
            return None
        delta = timezone.now() - self.last_confirmed_at
        return delta.days

    def has_recent_interaction(self, days: int = 60) -> bool:
        """Check if the record has had a recent interaction.

        Args:
            days: The number of days to consider as "recent". Defaults to 60.

        Returns:
            True if the last interaction occurred within the specified days,
            False otherwise.
        """
        if not self.last_confirmed_at:
            return False
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.last_confirmed_at >= cutoff

    def confirm(self) -> None:
        """Confirm the record and set the last interaction time.

        This method sets both confirmed_at and last_confirmed_at timestamps
        to the current time, marking the record as confirmed and recording
        the confirmation as an interaction.

        It only updates records that are not already confirmed, ensuring
        idempotency and preventing re-confirmation.

        Raises:
            BusinessError: If the record is not saved (no primary key) or
                is already confirmed.
        """
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        now = timezone.now()
        total_count = self.__class__.objects.model._base_manager.filter(
            pk=self.pk, confirmed_at__isnull=True
        ).update(confirmed_at=now, last_confirmed_at=now)

        if total_count == 0:
            raise BusinessError(ResourceAlreadyConfirmed())

    def update_interaction(self) -> None:
        """Update the last interaction timestamp.

        This method updates the last_confirmed_at field to the current time,
        indicating a successful interaction (e.g., OTP verification, login).

        It only updates records that are already confirmed, ensuring that
        interaction tracking is only maintained for verified records.

        Raises:
            BusinessError: If the record is not saved (no primary key) or
                is not yet confirmed.
        """
        if self.pk is None:
            raise BusinessError(ResourceNotSaved())

        total_count = self.__class__.objects.model._base_manager.filter(
            pk=self.pk, confirmed_at__isnull=False
        ).update(
            last_confirmed_at=timezone.now(),
        )

        if total_count == 0:
            raise BusinessError(ResourceNotConfirmed())
