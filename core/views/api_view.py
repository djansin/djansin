"""Provide an envelope-aware base view for non-model DRF endpoints.

Enveloping is opt-in via :meth:`APIView.build_response`; direct
``Response`` returns are passed through unchanged so this class stays a
drop-in replacement for DRF's ``APIView``.
"""

from typing import Any, overload

from rest_framework.views import APIView as DrfAPIView

from .mixins import ResponseEnvelopeMixin
from .responses import Response


class APIView(ResponseEnvelopeMixin, DrfAPIView):
    """Envelope-aware base view for non-model DRF endpoints.

    Enveloping is opt-in: only responses built through
    ``build_response`` are enveloped. Responses returned directly as
    ``Response`` instances are left untouched, keeping the class a
    drop-in replacement for DRF's ``APIView``.
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
        """Build an enveloped ``Response``.

        Args:
            message: Value for ``message``. Falls back to
                ``envelope_message`` when falsy.
            code: Value for ``code``. Falls back to ``envelope_code``
                when falsy.
            data: Payload to place under the envelope's ``data`` field.
            **kwds: Forwarded to the ``Response`` constructor.

        Returns:
            A new enveloped response.
        """
        return self._envelope_response(Response(data, **kwds), message, code)
