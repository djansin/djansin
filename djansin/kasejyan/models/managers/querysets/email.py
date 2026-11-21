"""QuerySet definitions for the kasejyan application's contact models.

This module exposes specialized QuerySet classes for contact-based models
(i.e. ``Email`` and ``Phone``) that inherit the reusable filtering and
chaining API provided by :class:`BaseQuerySet`.
"""

from core.models.managers.querysets import BaseQuerySet
from core.models.managers.querysets.mixins import BlockableQuerySetMixin


class EmailQuerySet(BlockableQuerySetMixin, BaseQuerySet):
    """QuerySet for the :class:`~djansin.kasejyan.models.Email` model.

    Inherits all chainable filtering helpers from
    :class:`~core.models.managers.querysets.BaseQuerySet` without
    introducing additional behavior. This class exists to provide a dedicated,
    strongly-typed QuerySet that can be extended with email-specific query
    methods in the future and to be referenced by
    :class:`~djansin.kasejyan.models.managers.email.EmailManager`.

    Attributes:
        Inherited from :class:`~core.models.managers.querysets.BaseQuerySet`.
    """

    pass
