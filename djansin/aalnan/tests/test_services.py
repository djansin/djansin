import pytest

from djansin.aalnan.models import Notification, NotificationType
from djansin.aalnan.services.notify import NotificationService


@pytest.fixture
def service():
    return NotificationService()


class TestNotificationService:
    def test_creates_notification(self, service, user):
        result = service(
            user=user,
            type=NotificationType.PASSWORD_CHANGED,
            title="Password changed",
            body="Your password was changed.",
        )

        assert result.title == "Password changed"
        assert Notification.objects.filter(user=user).count() == 1

    def test_rejects_inactive_user(self, service, user):
        user.is_active = False
        user.save(update_fields=["is_active"])

        with pytest.raises(Exception):
            service(
                user=user,
                type=NotificationType.LOGIN,
                title="x",
                body="y",
            )
