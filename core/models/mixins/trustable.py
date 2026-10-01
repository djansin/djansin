"""Trustable model mixin providing trust level classification and management.

This module defines an abstract model mixin that adds trust level classification
to Django models. Trust levels represent the degree of trust assigned to a
resource and are commonly used for access control, risk assessment, and
security policy enforcement.

The mixin provides a comprehensive API for managing trust levels including
elevation, lowering, and checking permissions based on trust thresholds.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.exceptions.common import AppError, BusinessError
from core.exceptions.errors.app import InvalidTrustLevel
from core.exceptions.errors.business import (
    TrustLevelElevation,
    TrustLevelElevationBeyondCore,
    TrustLevelLowering,
    TrustLevelLoweringBelowUntrusted,
)
from core.models.mixins.abstract import AbstractModelMixin


class TrustableMixin(AbstractModelMixin):
    """An abstract model mixin that adds trust level classification and management.

    This mixin extends AbstractModelMixin with trust level capabilities,
    providing a four-level classification system:
    - UNTRUSTED: New or unverified, lowest trust
    - REGULAR: Normal trust level for standard users
    - TRUSTED: Elevated trust with additional privileges
    - CORE: Highest trust for critical or power users

    Key features:
    - Trust level management (elevation, lowering, reset)
    - Permission checking based on trust thresholds
    - Trust level querying and validation
    - List of available trust levels and their properties
    - Convenience methods for common trust operations

    The mixin is typically used for:
    - Access control decisions (feature gating)
    - Risk assessment and scoring
    - Security policy enforcement
    - User reputation systems

    Attributes:
        trust_level: A PositiveSmallIntegerField storing the trust level.
            Uses TrustLevel choices with default UNTRUSTED.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.

    TrustLevel:
        An IntegerChoices enumeration defining the four trust levels:
        - UNTRUSTED (0): Lowest trust
        - REGULAR (1): Normal trust
        - TRUSTED (2): Elevated trust
        - CORE (3): Highest trust
    """

    class TrustLevel(models.IntegerChoices):
        """Trust level classification for verifiable resources.

        These levels represent the degree of trust assigned to a resource
        (email address, phone number, etc.) and can be used for:
        - Access control decisions
        - Risk assessment and scoring
        - Feature availability based on trust
        - Security policy enforcement

        The levels are ordered from least to most trusted:
        - UNTRUSTED: New or unverified, lowest trust
        - REGULAR: Normal trust level for standard users
        - TRUSTED: Elevated trust with additional privileges
        - CORE: Highest trust for critical or power users
        """

        UNTRUSTED = 0, _t("Untrusted")
        REGULAR = 1, _t("Regular")
        TRUSTED = 2, _t("Trusted")
        CORE = 3, _t("Core")

    trust_level = models.PositiveSmallIntegerField(
        choices=TrustLevel,
        default=TrustLevel.UNTRUSTED,
        verbose_name=_t("Trust Level"),
        help_text=_t(
            "Trust level assigned to this resource, affecting access control and security policies."
        ),
    )

    class Meta:
        """Metadata configuration for TrustableMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides trust level fields to all inheriting models.
        """

        abstract = True

    # ========== Class Methods for Queryset Helpers ==========

    @classmethod
    def get_trust_level_choices(cls) -> list[tuple[int, str]]:
        """Get all trust level choices as a list of (value, label) tuples.

        Returns:
            A list of tuples containing trust level values and their labels.
        """
        return cls.TrustLevel.choices

    @classmethod
    def get_trust_level_names(cls) -> list[str]:
        """Get all trust level labels.

        Returns:
            A list of all trust level label strings.
        """
        return [label for value, label in cls.TrustLevel.choices]

    @classmethod
    def get_trust_level_values(cls) -> list[int]:
        """Get all trust level values.

        Returns:
            A list of all trust level integer values.
        """
        return cls.TrustLevel.values

    @classmethod
    def get_trust_level_by_name(cls, name: str) -> int:
        """Get the trust level value by its name or label.

        Args:
            name: The trust level name or label to look up.

        Returns:
            The integer value of the matching trust level.

        Raises:
            AppError: If the provided name does not match any trust level.
        """
        for value, label in cls.TrustLevel.choices:
            if name in {label, value}:
                return value
        raise AppError(
            _t("Invalid trust level name: '{name}'."),
            name=name,
            _code=InvalidTrustLevel.code,
            _http_status=InvalidTrustLevel.http_status,
        )

    # ========== Properties ==========

    @property
    def is_untrusted(self) -> bool:
        """Check if the current trust level is UNTRUSTED.

        Returns:
            True if trust_level equals UNTRUSTED, False otherwise.
        """
        return self.trust_level == self.TrustLevel.UNTRUSTED

    @property
    def is_regular(self) -> bool:
        """Check if the current trust level is REGULAR.

        Returns:
            True if trust_level equals REGULAR, False otherwise.
        """
        return self.trust_level == self.TrustLevel.REGULAR

    @property
    def is_trusted(self) -> bool:
        """Check if the current trust level is TRUSTED.

        Returns:
            True if trust_level equals TRUSTED, False otherwise.
        """
        return self.trust_level == self.TrustLevel.TRUSTED

    @property
    def is_core(self) -> bool:
        """Check if the current trust level is CORE.

        Returns:
            True if trust_level equals CORE, False otherwise.
        """
        return self.trust_level == self.TrustLevel.CORE

    @property
    def has_high_trust(self) -> bool:
        """Check if the current trust level is TRUSTED or higher.

        Returns:
            True if trust_level >= TRUSTED, False otherwise.
        """
        return self.trust_level >= self.TrustLevel.TRUSTED

    @property
    def has_core_or_above(self) -> bool:
        """Check if the current trust level is CORE or higher.

        Returns:
            True if trust_level >= CORE, False otherwise.
        """
        return self.trust_level >= self.TrustLevel.CORE

    @property
    def trust_level_name(self) -> str:
        """Get the display name of the current trust level.

        Returns:
            The human-readable label for the current trust level.
        """
        return self.get_trust_level_display()

    @property
    def can_elevate_to(self) -> list[int]:
        """Get all trust levels that can be elevated to from the current level.

        Returns:
            A list of trust level values that are higher than the current level.
        """
        return [level for level in self.TrustLevel.values if level > self.trust_level]

    @property
    def can_lower_to(self) -> list[int]:
        """Get all trust levels that can be lowered to from the current level.

        Returns:
            A list of trust level values that are lower than the current level.
        """
        return [level for level in self.TrustLevel.values if level < self.trust_level]

    def has_minimum_trust(self, min_level: int) -> bool:
        """Check if the current trust level meets or exceeds a minimum threshold.

        Args:
            min_level: The minimum trust level required.

        Returns:
            True if trust_level >= min_level, False otherwise.
        """
        return self.trust_level >= min_level

    # ========== Trust Level Management ==========

    def set_trust_level(self, new_level: int, save: bool = True) -> None:
        """Set the trust level to a specific value.

        Args:
            new_level: The new trust level value to set.
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            AppError: If the provided trust level is invalid.
        """
        if new_level not in self.TrustLevel.values:
            raise AppError(
                InvalidTrustLevel(
                    new_level=new_level,
                    allowed_levels=list(self.TrustLevel.values),
                )
            )

        self.trust_level = new_level
        if save:
            self.save(update_fields=["trust_level"])

    def elevate_trust(self, new_level: int | None = None, save: bool = True) -> None:
        """Elevate the trust level by one or to a specific higher level.

        Args:
            new_level: The target trust level to elevate to. If None,
                elevates by one level. Defaults to None.
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If already at maximum level or trying to elevate
                to a level that is not higher than the current level.
            AppError: If the provided trust level is invalid.
        """
        if new_level is None:
            # Elevate by one level
            current_index = list(self.TrustLevel.values).index(self.trust_level)
            if current_index >= len(self.TrustLevel.values) - 1:
                raise BusinessError(TrustLevelElevationBeyondCore())
            new_level = self.TrustLevel.values[current_index + 1]
        if new_level not in self.TrustLevel.values:
            raise AppError(
                InvalidTrustLevel(
                    new_level=new_level,
                    allowed_levels=list(self.TrustLevel.values),
                )
            )
        if new_level <= self.trust_level:
            raise BusinessError(
                TrustLevelElevation(
                    new_level=new_level,
                    current_level=self.trust_level,
                )
            )

        self.set_trust_level(new_level=new_level, save=save)

    def lower_trust(self, new_level: int | None = None, save: bool = True) -> None:
        """Lower the trust level by one or to a specific lower level.

        Args:
            new_level: The target trust level to lower to. If None,
                lowers by one level. Defaults to None.
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If already at minimum level or trying to lower
                to a level that is not lower than the current level.
            AppError: If the provided trust level is invalid.
        """
        if new_level is None:
            # Lower by one level
            current_index = list(self.TrustLevel.values).index(self.trust_level)
            if current_index <= 0:
                raise BusinessError(TrustLevelLoweringBelowUntrusted())
            new_level = self.TrustLevel.values[current_index - 1]
        if new_level not in self.TrustLevel.values:
            raise AppError(
                InvalidTrustLevel(
                    new_level=new_level,
                    allowed_levels=list(self.TrustLevel.values),
                )
            )
        if new_level >= self.trust_level:
            raise BusinessError(
                TrustLevelLowering(
                    new_level=new_level,
                    current_level=self.trust_level,
                )
            )

        self.set_trust_level(new_level=new_level, save=save)

    def reset_trust(self, save: bool = True) -> None:
        """Reset the trust level to UNTRUSTED.

        Args:
            save: If True, saves the changes immediately. Defaults to True.
        """
        self.set_trust_level(self.TrustLevel.UNTRUSTED.value, save=save)

    def promote_to_regular(self, save: bool = True) -> None:
        """Promote the trust level to REGULAR.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If promotion is not allowed.
        """
        self.elevate_trust(self.TrustLevel.REGULAR.value, save=save)

    def promote_to_trusted(self, save: bool = True) -> None:
        """Promote the trust level to TRUSTED.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If promotion is not allowed.
        """
        self.elevate_trust(self.TrustLevel.TRUSTED.value, save=save)

    def promote_to_core(self, save: bool = True) -> None:
        """Promote the trust level to CORE.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If promotion is not allowed.
        """
        self.elevate_trust(self.TrustLevel.CORE.value, save=save)

    def demote_to_untrusted(self, save: bool = True) -> None:
        """Demote the trust level to UNTRUSTED.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If demotion is not allowed.
        """
        self.lower_trust(self.TrustLevel.UNTRUSTED.value, save=save)

    def demote_to_regular(self, save: bool = True) -> None:
        """Demote the trust level to REGULAR.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If demotion is not allowed.
        """
        self.lower_trust(self.TrustLevel.REGULAR.value, save=save)

    def demote_to_trusted(self, save: bool = True) -> None:
        """Demote the trust level to TRUSTED.

        Args:
            save: If True, saves the changes immediately. Defaults to True.

        Raises:
            BusinessError: If demotion is not allowed.
        """
        self.lower_trust(self.TrustLevel.TRUSTED.value, save=save)

    # ========== Permission / Access Control Methods ==========

    def is_allowed_for(self, required_level: int) -> bool:
        """Check if the current trust level meets the required threshold.

        Args:
            required_level: The minimum trust level required for access.

        Returns:
            True if trust_level >= required_level, False otherwise.
        """
        return self.trust_level >= required_level

    def is_allowed_for_regular(self) -> bool:
        """Check if the current trust level allows REGULAR access.

        Returns:
            True if trust_level >= REGULAR, False otherwise.
        """
        return self.is_allowed_for(self.TrustLevel.REGULAR.value)

    def is_allowed_for_trusted(self) -> bool:
        """Check if the current trust level allows TRUSTED access.

        Returns:
            True if trust_level >= TRUSTED, False otherwise.
        """
        return self.is_allowed_for(self.TrustLevel.TRUSTED.value)

    def is_allowed_for_core(self) -> bool:
        """Check if the current trust level allows CORE access.

        Returns:
            True if trust_level >= CORE, False otherwise.
        """
        return self.is_allowed_for(self.TrustLevel.CORE.value)
