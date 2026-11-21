"""Manager definitions for the :class:`~djansin.kasejyan.models.Phone` model.

This module exposes :class:`PhoneManager`, the default manager for the
``Phone`` model. It binds the model to :class:`PhoneQuerySet` and provides
high-level, number-based lookup helpers used by kasejyan services.
"""

from typing import TYPE_CHECKING

from core.models.managers import BaseManager
from core.models.managers.mixins import BlockableManagerMixin
from djansin.kasejyan.models.managers.querysets.phone import PhoneQuerySet


if TYPE_CHECKING:
    from djansin.kasejyan.models import Phone


class PhoneManager(BlockableManagerMixin[PhoneQuerySet], BaseManager[PhoneQuerySet]):
    """Manager for the :class:`~djansin.kasejyan.models.Phone` model.

    Wires the ``Phone`` model to :class:`PhoneQuerySet` and exposes
    convenience methods for retrieving phone records by their number. All
    querysets produced by this manager are instances of
    :class:`PhoneQuerySet`, preserving the chainable helper API.

    Attributes:
        Inherited from :class:`~core.models.managers.BaseManager`.
    """

    def get_queryset(self) -> PhoneQuerySet:
        """Return the base queryset for the ``Phone`` model.

        Returns:
            PhoneQuerySet: A queryset bound to the manager's database alias,
            typed as :class:`PhoneQuerySet`.
        """
        return PhoneQuerySet(self.model, using=self._db)

    def find_by_number(self, number: str) -> Phone | None:
        """Retrieve a single phone record by its number.

        Args:
            number (str): The phone number to look up. Comparison is exact
                and case-sensitive as stored in the database.

        Returns:
            Phone | None: The matching :class:`~djansin.kasejyan.models.Phone`
            instance, or ``None`` if no record with the given number exists.
        """
        return self.get_queryset().filter(number=number).first()
