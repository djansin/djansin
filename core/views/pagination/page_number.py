"""Pre-configured pagination profiles for common use cases.

Each profile subclasses :class:`PageNumberPagination` and tunes
``page_size`` / ``max_page_size`` for a specific workload (e.g. admin
reports, mobile clients, browse views).

Use these classes directly via ``pagination_class`` on views, or as
building blocks for project-specific variants.
"""

from core.views.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Default pagination profile for most list endpoints.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 20
    max_page_size = 50


class SmallResultsSetPagination(PageNumberPagination):
    """Compact profile for endpoints returning few items.

    Suitable for categories, tags, or quick-search results where
    large pages add no value.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 10
    max_page_size = 50


class StandardPagination(PageNumberPagination):
    """Standard profile for general-purpose list endpoints.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 20
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Profile for heavy endpoints returning large result sets.

    Intended for reports, audit logs, or admin exports where clients
    legitimately need many items per page.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 1000
    max_page_size = 10000


class CompactPagination(PageNumberPagination):
    """Lightweight profile for mobile, widgets, or bandwidth-sensitive clients.

    HTML pagination controls are disabled in the browsable API by setting
    ``template`` to ``None``, producing a pure-API response.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
        template (None): Disables rendered HTML pagination controls.
    """

    page_size = 5
    max_page_size = 20
    template = None


class BrowsePagination(PageNumberPagination):
    """Profile for browse/explore UIs that balance scrolling and loading.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 30
    max_page_size = 200


class NoCountPagination(PageNumberPagination):
    """Profile that omits the total ``count`` from the response.

    Suitable for very large tables where ``COUNT(*)`` is expensive and
    clients do not rely on knowing the total number of records.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
    """

    page_size = 20
    max_page_size = 100

    def get_meta(self) -> dict:
        """Returns metadata without the total count.

        Returns:
            dict: Metadata containing only ``next`` and ``previous`` links.
        """
        return {
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }


class WindowPagination(PageNumberPagination):
    """Profile exposing a sliding window of page numbers around the current page.

    Designed for UIs that render a limited set of page numbers (e.g.
    ``... 4 5 [6] 7 8 ...``) instead of the full range. The window size
    is controlled by :attr:`window`.

    Attributes:
        page_size (int): Items per page by default.
        max_page_size (int): Maximum items a client may request.
        window (int): Number of pages to include before and after the
            current page.
    """

    page_size = 20
    max_page_size = 100
    window = 2

    def get_meta(self) -> dict:
        """Returns windowed pagination metadata.

        Computes the visible page window around the current page and
        includes total counts and navigation links.

        Returns:
            dict: Metadata containing ``count``, ``num_pages``,
            ``current_page``, ``window_pages`` (list of visible page
            numbers), ``next``, and ``previous``.
        """
        current = self.page.number
        total = self.page.paginator.num_pages
        start = max(1, current - self.window)
        end = min(total, current + self.window)

        window_pages = list(range(start, end + 1))

        return {
            "count": self.page.paginator.count,
            "num_pages": total,
            "current_page": current,
            "window_pages": window_pages,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }
