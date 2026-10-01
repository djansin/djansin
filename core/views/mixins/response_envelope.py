"""Provide a mixin that wraps successful DRF responses in a standard envelope.

The envelope normalizes the shape of every 2xx payload returned by views
that mix this class in, so API clients can rely on a single top-level
structure regardless of the underlying view. Non-2xx responses, empty
bodies (204/304), and payloads that already carry the envelope are
passed through untouched.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from core.views.responses import Response


class ResponseEnvelopeMixin:
    """Wrap successful DRF responses in the project's standard envelope.

    Only ``response.data`` is rewritten, and only for 2xx responses.
    Status code, headers, renderer, and the ``Response`` instance are
    left untouched. Non-2xx responses, empty bodies (204/304), and
    payloads that already carry the envelope pass through unchanged.

    Paginated payloads (``results`` key) are unwrapped into ``items``,
    with ``count``, ``next``, and ``previous`` lifted into ``meta.pagination``.

    Attributes:
        envelope_code: Default value for the envelope's ``code`` field.
        envelope_message: Default value for the envelope's ``message``
            field.
    """

    envelope_code = "REQUEST_SUCCESS"
    envelope_message = _t("Operation completed successfully.")

    def _envelope_response(
        self,
        response: Response,
        message: str | None = None,
        code: str | None = None,
    ) -> Response:
        """Wrap ``response.data`` in the project's standard envelope.

        Falsy ``message`` and ``code`` fall back to ``envelope_message``
        and ``envelope_code`` respectively. Non-2xx responses, 204/304
        responses, and already-enveloped payloads pass through unchanged.
        Paginated payloads are unwrapped into ``items`` with pagination
        metadata lifted into ``meta.pagination``.

        Args:
            response: The DRF response to envelope.
            message: Value for ``message``. Falls back to
                ``envelope_message`` when falsy.
            code: Value for ``code``. Falls back to ``envelope_code``
                when falsy.

        Returns:
            The same response instance, with ``data`` enveloped for 2xx
            responses.
        """
        if response.status_code in (204, 304):
            return response

        if not (200 <= response.status_code < 300):
            return response

        if not hasattr(response, "data"):
            return response

        message = message or self.__class__.envelope_message
        code = code or self.__class__.envelope_code

        data = response.data
        # Already enveloped: nothing to do.
        if isinstance(data, dict) and {"code", "message"}.issubset(data.keys()):
            return response

        pagination = None
        if isinstance(data, dict) and "results" in data:
            pagination = {
                "count": data.get("count"),
                "next": data.get("next"),
                "previous": data.get("previous"),
            }
            data = {"items": data["results"]}

        envelope = {
            "code": code,
            "message": message,
            "data": data,
            "meta": {
                **({"pagination": pagination} if pagination else {}),
                "timestamp": timezone.now(),
            },
        }

        response.data = envelope

        return response
