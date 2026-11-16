from collections.abc import Callable
from dataclasses import asdict, fields, is_dataclass
from typing import Any

from core.exceptions import ValidationError
from core.exceptions.errors.validation import InvalidType


class ToDictMixin:
    """Adds a configurable ``to_dict`` to dataclass instances.

    For each dataclass field, if a method named ``<prefix><field_name>``
    exists, its return value is used instead of the raw attribute value.
    The method is called as ``method(value)`` where ``value`` is the raw
    field value.
    """

    _serializer_prefix: str = "get_"

    def to_dict(self) -> dict:
        if not is_dataclass(self):
            raise ValidationError(
                InvalidType(
                    expected_type="dataclass",
                    actual_type=type(self).__name__,
                )
            )

        result: dict[str, Any] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            serializer = self._resolve_serializer(field.name)
            result[field.name] = (
                serializer(value) if serializer else self._default_serialize(value)
            )
        return result

    def _resolve_serializer(self, field_name: str) -> Callable[[Any], Any] | None:
        """Return the per-field serializer method, or ``None`` if absent."""
        method_name = f"{self._serializer_prefix}{field_name}"
        method = getattr(self, method_name, None)

        if method is None:
            return None

        if not callable(method):
            raise ValidationError(
                InvalidType(
                    expected_type=f"callable method '{method_name}'",
                    actual_type=type(method).__name__,
                )
            )

        return method

    @staticmethod
    def _default_serialize(value: Any) -> Any:
        """Fallback serialization for fields without a dedicated serializer."""
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)

        return value
