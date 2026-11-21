"""Manager definitions for the :class:`~djansin.kasejyan.models.Email` model.

This module exposes :class:`EmailManager`, the default manager for the
``Email`` model. It binds the model to :class:`EmailQuerySet` and provides
high-level, address-based lookup helpers used by kasejyan services.
"""

from typing import TYPE_CHECKING

from core.models.managers import BaseManager
from core.models.managers.mixins import BlockableManagerMixin
from djansin.kasejyan.models.managers.querysets.email import EmailQuerySet


if TYPE_CHECKING:
    from djansin.kasejyan.models import Email


class EmailManager(BlockableManagerMixin[EmailQuerySet], BaseManager[EmailQuerySet]):
    """Manager for the :class:`~djansin.kasejyan.models.Email` model.

    Wires the ``Email`` model to :class:`EmailQuerySet` and exposes
    convenience methods for retrieving email records by their address. All
    querysets produced by this manager are instances of
    :class:`EmailQuerySet`, preserving the chainable helper API.

    Attributes:
        Inherited from :class:`~core.models.managers.BaseManager`.
    """

    def get_queryset(self) -> EmailQuerySet:
        """Return the base queryset for the ``Email`` model.

        Returns:
            EmailQuerySet: A queryset bound to the manager's database alias,
            typed as :class:`EmailQuerySet`.
        """
        return EmailQuerySet(self.model, using=self._db)

    def find_by_address(self, address: str) -> Email | None:
        """Retrieve a single email record by its address.

        Args:
            address (str): The email address to look up. Comparison is exact
                and case-sensitive as stored in the database.

        Returns:
            Email | None: The matching :class:`~djansin.kasejyan.models.Email`
            instance, or ``None`` if no record with the given address exists.
        """
        return self.get_queryset().filter(address=address).first()
