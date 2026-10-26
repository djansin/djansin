"""Pagination style implementations used across the project.

All classes in this module inherit from
:class:`~core.views.pagination.mixins.BaseMetaPaginationMixin` to enforce
the project's standard response envelope (``items`` + ``meta``).

Each concrete class delegates to a DRF built-in pagination class for
queryset slicing and link generation, and only customizes the ``meta``
payload via :meth:`get_meta`.
"""

from rest_framework.pagination import (
    CursorPagination as DrfCursorPagination,
    LimitOffsetPagination as DrfLimitOffsetPagination,
    PageNumberPagination as DrfPageNumberPagination,
)

from core.views.pagination.mixins import BaseMetaPaginationMixin


class PageNumberPagination(BaseMetaPaginationMixin, DrfPageNumberPagination):
    """Page-number pagination with a project-standard response envelope.

    Clients navigate with ``?page=N`` and may optionally control page size
    with ``?page_size=N`` (subject to ``max_page_size``).

    Attributes:
        page_size_query_param (str): Query parameter used to override page
            size per request.
        ordering (str): Default ordering applied when paginating.
    """

    page_size_query_param = "page_size"
    ordering = "-created_at"

    def get_meta(self) -> dict:
        """Returns page-number metadata.

        Returns:
            dict: Metadata containing ``count`` (total records),
            ``next`` (URL of the next page or ``None``), and ``previous``
            (URL of the previous page or ``None``).
        """
        return {
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }


class LimitOffsetPagination(BaseMetaPaginationMixin, DrfLimitOffsetPagination):
    """Limit/offset pagination with a project-standard response envelope.

    Clients navigate with ``?limit=N&offset=M``. Both parameters are
    optional and governed by ``default_limit`` and ``max_limit``.

    Attributes:
        offset_query_param (str): Query parameter for the offset.
        limit_query_param (str): Query parameter for the limit.
        ordering (str): Default ordering applied when paginating.
    """

    offset_query_param = "offset"
    limit_query_param = "limit"
    ordering = "-created_at"

    def get_meta(self) -> dict:
        """Returns limit/offset metadata.

        Returns:
            dict: Metadata containing ``count``, ``limit``, ``offset``,
            ``next``, and ``previous``.
        """
        return {
            "count": self.count,
            "limit": self.limit,
            "offset": self.offset,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }


class CursorPagination(BaseMetaPaginationMixin, DrfCursorPagination):
    """Cursor pagination with a project-standard response envelope.

    Clients navigate with an opaque ``?cursor=...`` token. This style is
    suited to large, stable-ordered datasets (e.g. timelines, feeds) where
    offset-based pagination becomes inefficient.

    Attributes:
        cursor_query_param (str): Query parameter for the cursor token.
        page_size_query_param (str): Query parameter for page size.
        ordering (str): Default ordering; must be unique and immutable
            (e.g. ``-created_at``).
    """

    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    ordering = "-created_at"

    def get_meta(self) -> dict:
        """Returns cursor metadata.

        Unlike page-number and limit/offset styles, no ``count`` is exposed
        because counting the full result set defeats the performance goals
        of cursor pagination.

        Returns:
            dict: Metadata containing ``page_size``, ``next``, and
            ``previous`` cursor links.
        """
        return {
            "page_size": self.page_size,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }
