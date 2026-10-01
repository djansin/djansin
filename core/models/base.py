"""Base concrete model combining timestamp fields, UUID identifier, and custom manager.

This module defines a foundational abstract model that serves as the primary
base class for all application models. It combines the timestamp tracking
from AbstractModel, the UUID identifier from BaseModelMixin, and a feature-rich
custom manager with common query utilities.

The model includes optimized database indexes to improve performance for
common query patterns such as retrieving recent records and time-based filtering.
"""

from core.models.abstract import AbstractModel
from core.models.managers.base import BaseManager
from core.models.mixins.base import BaseModelMixin


class BaseModel(BaseModelMixin, AbstractModel):
    """A comprehensive base model providing timestamp fields, UUID, and custom manager.

    This abstract model inherits from both BaseModelMixin and AbstractModel to
    provide a complete set of features for application models:

    - Automatic timestamp tracking (created_at, updated_at) from AbstractModel
    - Public UUID identifier for external references from BaseModelMixin
    - Custom BaseManager with query utilities (find_by_id, find_latest, count_all, etc.)
    - Optimized database indexes for performance

    The model is abstract, serving as a template for concrete models rather
    than creating its own database table. All inheriting models will have the
    timestamp fields, UUID identifier, and manager methods available.

    Attributes:
        objects: The custom BaseManager instance bound to this model,
            providing methods like find_by_id(), find_latest(), count_all(),
            and other query utilities defined in BaseManager and its parent classes.

        uuid: UUIDField inherited from BaseModelMixin.
            Public immutable identifier for external references.
            Generated automatically using uuid.uuid7() on creation.

        created_at: DateTimeField inherited from AbstractModelMixin.
            Automatically set on creation and not editable.

        updated_at: DateTimeField inherited from AbstractModelMixin.
            Automatically updated on every save operation.
    """

    objects: BaseManager = BaseManager()

    class Meta:
        """Metadata configuration for BaseModel.

        Makes this model abstract so it doesn't create a database table,
        but provides fields and manager to all inheriting models.

        Includes a database index on created_at (descending order) to
        improve performance for queries that retrieve the most recent
        records. This index optimizes common query patterns such as:
        - Listing the most recent records
        - Time-based filtering and counting
        - Pagination by creation date
        - Sorting by newest first (order_by_newest())
        """

        abstract = True
