"""Typed result objects for the ``aalnan`` app."""

from dataclasses import dataclass
from datetime import datetime

from core.types import Result


@dataclass(frozen=True, slots=True)
class NotificationResult(Result):
    """A single notification, serializable for API responses."""

    id: int
    type: str
    title: str
    body: str
    data: dict
    is_read: bool
    created_at: datetime

    def get_created_at(self, value: datetime) -> str:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class NotificationListResult(Result):
    """A page of notifications with pagination metadata."""

    count: int
    unread_count: int
    results: list[NotificationResult]

    def get_results(self, value: list[NotificationResult]) -> list[dict]:
        return [n.to_dict() for n in value]


@dataclass(frozen=True, slots=True)
class NotificationPreferenceResult(Result):
    """The user's notification channel preferences."""

    in_app_enabled: bool
    email_enabled: bool
    sms_enabled: bool
