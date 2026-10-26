"""Base API view with JWT authentication and a unified response builder.

This module defines ``APIView``, a project-wide base class for class-based
views. It combines JWT authentication (via ``JWTAuthMixin``) with a
``build_response`` helper that emits a consistent envelope of
``{"code", "message", "data"}`` across all endpoints.

Typical usage example:

    from core.views.api import APIView

    class HealthView(APIView):
        def get(self, request):
            return self.build_response(
                message="OK",
                code="health_ok",
                data={"status": "up"},
            )
"""

from typing import Any, overload

from rest_framework.views import APIView as DrfAPIView

from core.views.mixins.auth import JWTAuthMixin
from core.views.responses import Response


class APIView(JWTAuthMixin, DrfAPIView):
    """Project base class for authenticated API views.

    Combines ``JWTAuthMixin`` (JWT authentication) with DRF's ``APIView``
    and exposes ``build_response`` to produce responses in a single,
    predictable envelope.

    All subclasses inherit:
        - JWT authentication on every request (via ``JWTAuthMixin``).
        - A standard response format produced by ``build_response``.

    Attributes:
        authentication_classes (list[type]): Inherited from
            ``JWTAuthMixin``; defaults to ``[JWTAuthentication]``.
    """

    @overload
    def build_response(
        self,
        message: str,
        code: str,
        data: Any | None = None,
        *,
        status: Any | None = None,
        template_name: Any | None = None,
        headers: Any | None = None,
        exception: bool = False,
        content_type: Any | None = None,
    ) -> Response: ...

    def build_response(
        self, message: str, code: str, data: Any | None = None, **kwds
    ) -> Response:
        """Build a standardized response envelope.

        Wraps the supplied payload in the project-wide response shape::

            {
                "code": <code>,
                "message": <message>,
                "data": <data>
            }

        Additional keyword arguments are forwarded verbatim to the
        underlying ``Response`` constructor, allowing callers to control
        HTTP status, headers, content type, template name, and whether the
        response represents an exception.

        Args:
            message: A human-readable message describing the outcome. Intended
                for clients to surface directly or to log.
            code: A stable machine-readable code identifying the outcome
                (e.g. ``"auth_invalid_token"``). Clients should branch on this
                value rather than on ``message``.
            data: The payload to return. May be any JSON-serializable value
                (dict, list, str, number, bool, or ``None``). Defaults to
                ``None`` when no payload is required.
            **kwds: Extra keyword arguments forwarded to ``Response``:
                - ``status``: HTTP status code or ``rest_framework.status`` value.
                - ``template_name``: Template used when rendering HTML.
                - ``headers``: Mapping of extra HTTP headers.
                - ``exception``: When ``True``, marks the response as an error
                  and instructs DRF to treat it as such (e.g. for exception
                  handlers).
                - ``content_type``: Explicit response content type.

        Returns:
            A ``core.views.responses.Response`` instance whose ``data`` is the
            ``{"code", "message", "data"}`` envelope described above.

        Example:
            >>> def get(self, request):
            ...     return self.build_response(
            ...         message="User fetched",
            ...         code="user_ok",
            ...         data={"id": 1},
            ...         status=200,
            ...     )
        """
        return Response(data={"code": code, "message": message, "data": data}, **kwds)
