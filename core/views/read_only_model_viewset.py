"""Provide an envelope-aware read-only model viewset.

Supplies ``ROModelViewSet``, a drop-in replacement for DRF's
``ReadOnlyModelViewSet`` that wraps every 2xx response in the project's
standard envelope via ``finalize_response``. Paginated payloads are
unwrapped into ``items`` with pagination metadata lifted into
``meta.pagination``.
"""

from typing import Any

from rest_framework.viewsets import ReadOnlyModelViewSet

from .mixins import ResponseEnvelopeMixin
from .responses import Response


class ROModelViewSet(ResponseEnvelopeMixin, ReadOnlyModelViewSet):
    """Read-only model viewset with automatic envelope responses.

    Every 2xx response is enveloped by ``finalize_response``. Paginated
    payloads are unwrapped into ``items`` with pagination metadata
    lifted into ``meta.pagination``.
    """

    def finalize_response(
        self,
        request: Any,
        response: Response,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Envelope the response body before it is rendered.

        Delegates to ``super().finalize_response`` first, then calls
        ``_envelope_response`` for 2xx responses.

        Args:
            request: The current DRF request.
            response: The DRF response produced by the viewset.
            *args: Forwarded to the parent implementation.
            **kwargs: Forwarded to the parent implementation.

        Returns:
            The same response instance, with ``data`` enveloped for 2xx
            responses.
        """
        response = super().finalize_response(request, response, *args, **kwargs)

        if 200 <= response.status_code < 300:
            self._envelope_response(response)

        return response
