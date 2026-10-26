"""Cross-source limit/offset pagination for merged or multi-origin feeds.

This module provides :class:`CrossPagination`, a specialization of
:class:`~core.views.pagination.LimitOffsetPagination` intended for endpoints
that stitch together results from multiple sources (or otherwise let the
client control an absolute position) via ``limit`` and ``offset``.
"""

from core.views.pagination import LimitOffsetPagination


class CrossPagination(LimitOffsetPagination):
    """Limit/offset pagination profile for cross-source or position-based feeds.

    This profile is designed for endpoints where the client drives an
    absolute position in the result set — for example, merged feeds that
    combine several querysets, infinite-scroll UIs, or clients that need
    to resume from a known offset.

    The response inherits the project's standard ``items``/``meta``
    envelope, including ``count``, ``limit``, ``offset``, ``next``, and
    ``previous``, plus the automatic ``timestamp``.

    Attributes:
        default_limit (int): Page size used when the client omits the
            ``limit`` query parameter.
        max_limit (int): Upper bound for the ``limit`` value a client may
            request, protecting the server from oversized pages.
    """

    default_limit = 20
    max_limit = 100
