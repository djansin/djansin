"""Base mixin for standardizing paginated API responses.

This module provides :class:`BaseMetaPaginationMixin`, a lightweight mixin
that enforces a consistent ``{"items": [...], "meta": {...}}`` envelope
across all pagination styles used in the project.

Pagination subclasses inherit from this mixin **first** in their MRO so
that :meth:`BaseMetaPaginationMixin.get_paginated_response` takes
precedence over the DRF default.
"""

from django.utils import timezone

from core.views.responses import Response


class BaseMetaPaginationMixin:
    """Standardizes paginated responses into an ``items``/``meta`` envelope.

    Subclasses must override :meth:`get_meta` to supply the pagination-style
    specific metadata (e.g. ``count``, ``limit``, ``cursor`` links). The
    base mixin automatically injects a ``timestamp`` field into ``meta``.

    Example:
        >>> class MyPagination(BaseMetaPaginationMixin, PageNumberPagination):
        ...     def get_meta(self):
        ...         return {"count": self.count}
    """

    def get_meta(self) -> dict:
        """Returns pagination-specific metadata.

        Subclasses override this method to expose their own fields. The
        returned mapping is merged into the ``meta`` object of the response.

        Returns:
            dict: A mapping of metadata keys (e.g. ``count``, ``next``,
            ``previous``) to their values. Defaults to an empty dict.
        """
        return {}

    def get_paginated_response(self, data: list):
        """Builds the standardized paginated response envelope.

        Calls :meth:`get_meta`, appends a ``timestamp`` field, and wraps the
        serialized page data into ``{"items": data, "meta": meta}``.

        Args:
            data (list): Serialized page data produced by the view.

        Returns:
            core.views.responses.Response: Response object containing the
            ``items`` list and the enriched ``meta`` mapping.
        """
        meta = self.get_meta()
        meta["timestamp"] = timezone.now()
        return Response({"items": data, "meta": meta})
