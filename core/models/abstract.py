"""Abstract base model providing timestamp fields, custom manager, and model introspection utilities.

This module defines a foundational abstract model that combines timestamp
tracking from AbstractModelMixin with a custom AbstractManager. It serves
as the base class for all application models, providing consistent timestamp
fields (created_at, updated_at) and a feature-rich manager with common
query utilities.

The model includes a database index on created_at in descending order to
optimize queries that sort by creation time (e.g., retrieving the most
recent records).

Additionally, this module provides model introspection utilities through
the ModelInfo dataclass, enabling consistent access to model metadata
such as verbose names and app labels.
"""

from dataclasses import dataclass

from django.db import models

from core.models.managers.abstract import AbstractManager
from core.models.mixins.abstract import AbstractModelMixin


class AbstractModel(AbstractModelMixin, models.Model):
    """An abstract base model that combines timestamp fields with a custom manager.

    This model inherits from AbstractModelMixin to provide automatic
    created_at and updated_at timestamp fields, and includes a custom
    AbstractManager that offers convenient query methods for ID-based
    filtering, time-based queries, ordering, and counting.

    The model is abstract, serving as a template for concrete models rather
    than creating its own database table. All inheriting models will have
    the timestamp fields and manager methods available.

    Additionally, this model provides introspection utilities for retrieving
    model metadata including verbose names, class names, and app labels,
    both at the class level and instance level.

    Attributes:
        objects: The custom AbstractManager instance bound to this model,
            providing methods like find_by_id(), find_latest(), count_all(),
            and other query utilities defined in AbstractManager.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    objects: AbstractManager = AbstractManager()

    class Meta:
        """Metadata configuration for AbstractModel.

        Makes this model abstract so it doesn't create a database table,
        but provides fields and manager to all inheriting models.

        Includes a database index on created_at (descending order) to
        improve performance for queries that retrieve the most recent
        records. The index name is dynamically generated using the
        application label and model class name to avoid collisions.
        """

        abstract = True

        indexes = [
            models.Index(
                fields=["-created_at"],
                name="%(app_label)s_%(class)s_time_idx",
            ),
        ]

    # ========== Model Name Methods ==========

    @classmethod
    def get_model_name(cls) -> str:
        """Get the verbose name of the model.

        Returns the model's verbose_name from Meta if available, otherwise
        returns the class name. Handles lazy translation objects properly.

        Returns:
            The verbose name of the model as a string.
        """
        if hasattr(cls, "_meta") and hasattr(cls._meta, "verbose_name"):
            # If verbose_name is a lazy translation object, convert it to string
            verbose_name = cls._meta.verbose_name
            if hasattr(verbose_name, "_proxy____code"):
                # It's a lazy translation, get the actual string
                return str(verbose_name)
            return verbose_name
        return cls.__name__

    @classmethod
    def get_model_name_plural(cls) -> str:
        """Get the plural verbose name of the model.

        Returns the model's verbose_name_plural from Meta if available,
        otherwise returns the class name. Handles lazy translation objects
        properly.

        Returns:
            The plural verbose name of the model as a string.
        """
        if hasattr(cls, "_meta") and hasattr(cls._meta, "verbose_name_plural"):
            verbose_name_plural = cls._meta.verbose_name_plural
            if hasattr(verbose_name_plural, "_proxy____code"):
                return str(verbose_name_plural)
            return verbose_name_plural
        return f"{cls.__name__}"

    @classmethod
    def get_model_info_class(cls) -> "ModelInfo":
        """Get a ModelInfo object containing all model metadata.

        Returns:
            A ModelInfo instance containing the model's verbose name,
            plural verbose name, class name, and app label.
        """
        return ModelInfo(
            verbose_name=cls.get_model_name(),
            verbose_name_plural=cls.get_model_name_plural(),
            class_name=cls.__name__,
            app_label=cls._meta.app_label if hasattr(cls._meta, "app_label") else None,
        )

    @property
    def verbose_name(self) -> str:
        """Get the verbose name of this model instance.

        Returns:
            The verbose name of the model as a string.
        """
        return self.get_model_name()

    @property
    def verbose_name_plural(self) -> str:
        """Get the plural verbose name of this model instance.

        Returns:
            The plural verbose name of the model as a string.
        """
        return self.get_model_name_plural()

    @property
    def instance_name(self) -> str:
        """Get a human-readable name for this instance.

        Combines the model's verbose name with the string representation
        of the instance.

        Returns:
            A formatted string containing the model name and instance
            representation (e.g., "User: john_doe").
        """
        model_name = self.get_model_name()
        instance_str = str(self)
        return f"{model_name}: {instance_str}"

    @property
    def instance_type(self) -> str:
        """Get the class name of this instance.

        Returns:
            The name of the instance's class.
        """
        return self.__class__.__name__

    @property
    def model_info(self) -> "ModelInfo":
        """Get a ModelInfo object for this instance.

        Returns:
            A ModelInfo instance containing this instance's model metadata.
        """
        return ModelInfo(
            verbose_name=self.verbose_name,
            verbose_name_plural=self.get_model_name_plural(),
            class_name=self.__class__.__name__,
            app_label=self._meta.app_label
            if hasattr(self._meta, "app_label")
            else None,
        )


@dataclass
class ModelInfo:
    """A dataclass for storing model metadata information.

    This class provides a structured way to store and access model
    metadata including verbose names, class names, and app labels.

    Attributes:
        verbose_name: The human-readable singular name of the model.
        verbose_name_plural: The human-readable plural name of the model.
        class_name: The Python class name of the model.
        app_label: The Django app label containing the model, if available.
    """

    verbose_name: str
    verbose_name_plural: str
    class_name: str
    app_label: str | None = None

    def __str__(self) -> str:
        """Get a string representation of the model info.

        Returns:
            A formatted string containing the verbose name and class name.
        """
        return f"{self.verbose_name} ({self.class_name})"

    def to_dict(self) -> dict:
        """Convert the ModelInfo to a dictionary.

        Returns:
            A dictionary containing all ModelInfo attributes.
        """
        return {
            "verbose_name": self.verbose_name,
            "verbose_name_plural": self.verbose_name_plural,
            "class_name": self.class_name,
            "app_label": self.app_label,
        }
