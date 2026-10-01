"""Abstract model mixin providing automatic timestamp fields for Django models.

This module defines a reusable abstract mixin that adds created_at and updated_at
timestamp fields to any model that inherits from it. The fields are automatically
managed by Django: created_at is set once upon object creation, and updated_at
is updated every time the object is saved. This mixin is designed to be used
as a base class for models that require auditing of creation and modification times.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _t


class AbstractModelMixin(models.Model):
    """An abstract model mixin that provides automatic timestamp tracking.

    This mixin adds two timestamp fields to models:
    - created_at: Automatically set to the current timestamp when the object is
      first created. This field is not editable after creation.
    - updated_at: Automatically updated to the current timestamp every time the
      object is saved.

    The mixin is abstract, meaning it does not create a database table on its own.
    Instead, it provides these fields to any concrete model that inherits from it.

    Attributes:
        created_at: A DateTimeField that stores the creation timestamp.
            Set automatically on object creation and not editable afterward.
        updated_at: A DateTimeField that stores the last modification timestamp.
            Updated automatically on every save operation.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_t("Created at"),
        help_text=_t("Timestamp when the object was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_t("Updated at"),
        help_text=_t("Timestamp when the object was last updated."),
    )

    class Meta:
        """Metadata configuration for AbstractModelMixin.

        Makes this model abstract so it doesn't create a database table,
        but provides timestamp fields to all inheriting models.
        """

        abstract = True
