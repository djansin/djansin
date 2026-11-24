import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from djansin.kasejyan.services.password_change import ChangePasswordService


@pytest.fixture
def service():
    return ChangePasswordService()


@pytest.fixture
def user_with_sessions(db, user):
    tokens = [RefreshToken.for_user(user) for _ in range(3)]
    return user, tokens


class TestChangePasswordService:
    def test_changes_password_and_revokes_other_sessions(
        self, service, user_with_sessions
    ):
        user, tokens = user_with_sessions
        current_jti = tokens[0]["jti"]

        result = service(
            user=user,
            current_password="secret123",
            new_password="newsecret456",
            current_jti=current_jti,
        )

        user.refresh_from_db()
        assert user.check_password("newsecret456")
        assert len(result.revoked_sessions) == 2
        assert all(s.jti != current_jti for s in result.revoked_sessions)

    def test_revokes_all_sessions_when_no_jti(self, service, user_with_sessions):
        user, tokens = user_with_sessions

        result = service(
            user=user,
            current_password="secret123",
            new_password="newsecret456",
        )

        assert len(result.revoked_sessions) == 3

    def test_rejects_wrong_current_password(self, service, user):
        with pytest.raises(Exception):
            service(user=user, current_password="wrong", new_password="newsecret456")

    def test_rejects_same_password(self, service, user):
        with pytest.raises(Exception):
            service(user=user, current_password="secret123", new_password="secret123")

    def test_rejects_weak_password(self, service, user):
        with pytest.raises(Exception):
            service(user=user, current_password="secret123", new_password="123")
