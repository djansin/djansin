import pytest

from djansin.kasejyan.services.username_change import ChangeUsernameService


@pytest.fixture
def service():
    return ChangeUsernameService()


class TestChangeUsernameService:
    def test_changes_username(self, service, user):
        result = service(user=user, new_username="newname")
        user.refresh_from_db()
        assert user.username == "newname"
        assert result.old_username == "testuser"
        assert result.new_username == "newname"

    def test_rejects_same_username(self, service, user):
        with pytest.raises(Exception):
            service(user=user, new_username="testuser")

    def test_rejects_taken_username(self, service, user, db):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user(username="taken", password="x")

        with pytest.raises(Exception):
            service(user=user, new_username="taken")

    def test_rejects_invalid_format(self, service, user):
        with pytest.raises(Exception):
            service(user=user, new_username="Invalid Name!")
