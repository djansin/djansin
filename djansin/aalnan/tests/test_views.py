from django.urls import reverse

from djansin.aalnan.models import Notification, NotificationType


class TestNotificationListView:
    def test_lists_notifications(self, auth_api):
        api, user = auth_api
        Notification.objects.create(
            user=user, type=NotificationType.LOGIN, title="t", body="b"
        )

        url = reverse("aalnan:list")
        resp = api.get(url)

        assert resp.status_code == 200
        assert resp.json()["data"]["count"] == 1


class TestNotificationReadView:
    def test_marks_read(self, auth_api):
        api, user = auth_api
        n = Notification.objects.create(
            user=user, type=NotificationType.LOGIN, title="t", body="b"
        )

        url = reverse("aalnan:read", kwargs={"pk": n.pk})
        resp = api.patch(url)

        assert resp.status_code == 200
        n.refresh_from_db()
        assert n.is_read is True


class TestNotificationReadAllView:
    def test_marks_all_read(self, auth_api):
        api, user = auth_api
        for _ in range(3):
            Notification.objects.create(
                user=user, type=NotificationType.LOGIN, title="t", body="b"
            )

        url = reverse("aalnan:read-all")
        resp = api.post(url)

        assert resp.status_code == 200
        assert Notification.objects.unread_for_user(user).count() == 0
