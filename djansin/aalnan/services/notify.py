"""Service layer for creating and dispatching notifications."""

from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError
from core.exceptions.errors.business import ResourceNotFound
from core.services import Service
from djansin.aalnan.models import Notification
from djansin.aalnan.types import NotificationResult
from djansin.kasejyan.models import User


class NotificationService(Service[NotificationResult]):
    """Create a notification for a user and dispatch it.

    Persists the notification, then — in phase 2 — pushes it over the
    user's WebSocket group. In phase 1, dispatch is a no-op; the
    notification is still available through the REST list endpoint.
    """

    def execute(
        self,
        *,
        user: User,
        type: str,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> NotificationResult:
        """Create a notification for ``user``.

        Args:
            user (User): The recipient.
            type (str): A :class:`NotificationType` value.
            title (str): Short, human-readable title.
            body (str): Full notification text.
            data (dict | None): Optional structured payload.

        Returns:
            NotificationResult: The created notification.

        Raises:
            BusinessError: If ``user`` does not exist or is inactive.
        """
        if user is None or not user.pk:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        if not user.is_active:
            raise BusinessError(ResourceNotFound(resource=_t("Active user")))

        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            body=body,
            data=data or {},
        )

        self._dispatch(notification)

        return self._to_result(notification)

    def _dispatch(self, notification: Notification) -> None:
        """Push the notification over the user's WebSocket group.

        TODO (phase 2): implement ``channel_layer.group_send`` to
        ``user_{user_id}``. Currently a no-op.
        """
        ...

    @staticmethod
    def _to_result(notification: Notification) -> NotificationResult:
        return NotificationResult(
            id=notification.pk,
            type=notification.type,
            title=notification.title,
            body=notification.body,
            data=notification.data,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )
