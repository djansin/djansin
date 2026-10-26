"""Authentication mixins for DRF-based views.

This module provides reusable mixins that configure authentication
behaviour for class-based views built on Django REST Framework.

Typical usage example:

    from core.views.mixins.auth import JWTAuthMixin

    class MyView(JWTAuthMixin, APIView):
        ...
"""

from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMixin:
    """Mixin that enforces JWT authentication on a DRF view.

    Sets ``authentication_classes`` to ``[JWTAuthentication]`` so that any
    view inheriting from this mixin requires a valid JWT bearer token in
    the ``Authorization`` header. Because authentication runs before
    permission and throttling checks, requests without a valid token are
    rejected at the authentication stage.

    This mixin is intended to be the first base class so that its
    ``authentication_classes`` attribute takes precedence in the MRO:

        class MyView(JWTAuthMixin, APIView):
            ...

    Attributes:
        authentication_classes (list[type]): A one-element list containing
            ``JWTAuthentication`` from ``rest_framework_simplejwt``.
    """

    authentication_classes = [JWTAuthentication]
