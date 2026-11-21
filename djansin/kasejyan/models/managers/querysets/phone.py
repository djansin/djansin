"""QuerySet definitions for phone-based contact lookups.

This module exposes the :class:`PhoneQuerySet`, a specialized QuerySet for the
:class:`~djansin.kasejyan.models.Phone` model. It inherits the full set of
chainable filtering helpers from
:class:`~core.models.managers.querysets.BaseQuerySet` and serves as the
dedicated query entry point for
:class:`~djansin.kasejyan.models.managers.phone.PhoneManager`.
"""

from core.models.managers.querysets import BaseQuerySet
from core.models.managers.querysets.mixins import BlockableQuerySetMixin


class PhoneQuerySet(BlockableQuerySetMixin, BaseQuerySet):
    """QuerySet for the :class:`~djansin.kasejyan.models.Phone` model.

    Inherits all filtering and chaining helpers from
    :class:`~core.models.managers.querysets.BaseQuerySet` without adding
    any behavior. This class exists to provide a dedicated, strongly-typed
    QuerySet that can be extended with phone-specific query methods in the
    future, and to be referenced as the queryset type of
    :class:`~djansin.kasejyan.models.managers.phone.PhoneManager`.

    Attributes:
        Inherited from
        :class:`~core.models.managers.querysets.BaseQuerySet`.
    """

    pass
