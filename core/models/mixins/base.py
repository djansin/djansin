"""Base model mixin providing a public UUID identifier for models.

This module defines an abstract mixin that extends AbstractModelMixin by adding
a UUID field. The UUID serves as a public, immutable identifier that can be
safely exposed in URLs, APIs, and external references without revealing
internal primary key values or order.

The mixin uses uuid.uuid7() which generates time-ordered UUIDs compatible with
UUID version 7, offering better database index performance than random UUIDs
while maintaining global uniqueness.
"""

import uuid as uuid_module

from django.db import models
from django.utils.translation import gettext_lazy as _t

from core.models.mixins.abstract import AbstractModelMixin


class BaseModelMixin(AbstractModelMixin):
    """An abstract model mixin that adds a public UUID identifier.

    This mixin builds upon AbstractModelMixin, inheriting the created_at and
    updated_at timestamp fields, and adds a UUID field that serves as a
    public, immutable identifier for each record.

    The UUID is automatically generated using uuid.uuid7() when the object
    is created. It is not editable after creation and is unique across all
    records. This field is ideal for use in public-facing contexts such as:
    - API endpoints (e.g., /api/v1/users/{uuid}/)
    - External system references
    - URLs that should not expose sequential primary keys
    - Audit trails and logging

    The field is explicitly marked as editable=False to ensure the identifier
    remains immutable throughout the object's lifecycle, maintaining referential
    integrity for external systems that rely on it.

    Attributes:
        uuid: A UUIDField storing the public immutable identifier.
            Generated automatically using uuid.uuid7() on creation.
            Unique across all records and not editable.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    uuid = models.UUIDField(
        default=uuid_module.uuid7,
        editable=False,
        unique=True,
        verbose_name=_t("uuid"),
        help_text=_t("Public immutable identifier for external references."),
    )

    class Meta:
        """Metadata configuration for BaseModelMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides fields to all inheriting models.
        """

        abstract = True
