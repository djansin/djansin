"""Read-only model viewset with JWT authentication, rate limiting, and pagination.

This module provides ``ReadOnlyModelViewSet``, a project base class for
read-only endpoints (``list`` and ``retrieve``). It enforces JWT
authentication, applies tiered rate limiting, and applies the project's
default pagination policy to list responses.

Typical usage example:

    from core.views.viewset import ReadOnlyModelViewSet

    class UserViewSet(ReadOnlyModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer

Note:
    Throttles are applied at the **view** level, not per-action. As a
    result, both ``list`` and ``retrieve`` requests consume the burst
    and sustained buckets inherited from ``RateLimitThrottleMixin``.
    Pagination, by contrast, only affects ``list`` responses.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet as DrfReadOnlyModelViewSet

from core.views.mixins.auth import JWTAuthMixin
from core.views.mixins.throttle import RateLimitThrottleMixin
from core.views.pagination import DefaultPagination


class ReadOnlyModelViewSet(
    JWTAuthMixin, RateLimitThrottleMixin, DrfReadOnlyModelViewSet
):
    """Read-only viewset with JWT authentication, throttling, and pagination.

    Extends DRF's ``ReadOnlyModelViewSet`` (which provides ``list`` and
    ``retrieve`` actions) with three project-wide defaults:

        1. JWT authentication on every request (via ``JWTAuthMixin``).
        2. Tiered rate limiting — anonymous, burst, and sustained — on
           every request, applied *before* the action body executes (via
           ``RateLimitThrottleMixin``).
        3. Pagination applied to ``list`` responses using
           ``DefaultPagination``.

    The MRO is::

        ReadOnlyModelViewSet
          ├─ JWTAuthMixin
          ├─ RateLimitThrottleMixin
          └─ rest_framework.viewsets.ReadOnlyModelViewSet

    Subclasses must define at least ``queryset`` and ``serializer_class``.

    Attributes:
        authentication_classes (list[type]): Inherited from
            ``JWTAuthMixin``; defaults to ``[JWTAuthentication]``.
        throttle_classes (list[type]): Inherited from
            ``RateLimitThrottleMixin``; applies anonymous, burst, and
            sustained throttles. Override per-viewset to customize the
            policy (e.g. relax the burst limit for a read-heavy
            endpoint).
        pagination_class (type): ``DefaultPagination``, applied
            automatically to the ``list`` action. Set to ``None`` on a
            subclass to disable pagination for that endpoint.

    Example:
        class UserViewSet(ReadOnlyModelViewSet):
            queryset = User.objects.order_by("id")
            serializer_class = UserSerializer

    Note:
        Because throttles are view-level, ``retrieve`` requests also
        count against the burst and sustained buckets. If ``retrieve``
        should not be throttled, override ``throttle_classes`` on the
        subclass or move the throttles into a custom ``get_throttles``
        implementation that inspects ``self.action``.
    """

    pagination_class = DefaultPagination
