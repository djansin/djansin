"""Base class for service-layer components.

This module defines :class:`BaseService`, a minimal, dependency-free base
class intended to be inherited by concrete service classes across the
project. It provides a shared marker type for service-layer components
without imposing any behavior.
"""


class BaseService:
    """Base class for all service-layer components.

    Serves as a common ancestor and marker type for service classes. It
    declares no attributes or methods, allowing subclasses to define their
    own public API while remaining identifiable as services (e.g. for
    type checks, documentation grouping, or shared mixins added later).
    """

    ...
