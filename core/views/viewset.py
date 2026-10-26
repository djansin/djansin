"""Read-only model viewset with JWT authentication and default pagination.

This module provides ``ReadOnlyModelViewSet``, a project base class for
read-only endpoints (``list`` and ``retrieve``). It enforces JWT
authentication and applies the project's default pagination policy.

Typical usage example:

    from core.views.viewset import ReadOnlyModelViewSet

    class UserViewSet(ReadOnlyModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
"""

from rest_framework.viewsets import ReadOnlyModelViewSet as DrfReadOnlyModelViewSet

from core.views.mixins.auth import JWTAuthMixin
from core.views.pagination import DefaultPagination


class ReadOnlyModelViewSet(JWTAuthMixin, DrfReadOnlyModelViewSet):
    """Read-only viewset with JWT authentication and default pagination.

    Extends DRF's ``ReadOnlyModelViewSet`` (which provides ``list`` and
    ``retrieve`` actions) with two project-wide defaults:

        1. JWT authentication on every request (via ``JWTAuthMixin``).
        2. Pagination applied to ``list`` responses using
           ``DefaultPagination``.

    Subclasses must define at least ``queryset`` and ``serializer_class``.

    Attributes:
        authentication_classes (list[type]): Inherited from
            ``JWTAuthMixin``; defaults to ``[JWTAuthentication]``.
        pagination_class (type): ``DefaultPagination``, applied automatically
            to the ``list`` action.

    Example:
        class UserViewSet(ReadOnlyModelViewSet):
            queryset = User.objects.order_by("id")
            serializer_class = UserSerializer
    """

    pagination_class = DefaultPagination
