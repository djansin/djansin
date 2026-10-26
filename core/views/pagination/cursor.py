"""Keyset (cursor) pagination profile for large, ordered datasets.

This module provides :class:`KeysetPagination`, a thin specialization of
:class:`~core.views.pagination.CursorPagination` that exposes a fixed page
size while inheriting the project's standard ``items``/``meta`` response
envelope.
"""

from core.views.pagination import CursorPagination


class KeysetPagination(CursorPagination):
    """Cursor pagination profile tuned for keyset-style navigation.

    Keyset pagination walks a result set in a stable order using an opaque
    cursor instead of numeric offsets. It is well suited to large tables
    (e.g. activity feeds, audit trails) where offset-based pagination
    becomes inefficient or unstable as records are inserted.

    This class relies on the parent's ``ordering`` (``-created_at``) and
    cursor mechanics, and only pins the page size to a sensible default.
    The ordering field must be unique and immutable for correct results.

    Attributes:
        page_size (int): Number of items returned per page. Inherited
            cursor query parameters and ordering are used as-is.
    """

    page_size = 20
