"""Tests for :class:`DeactivateAccountService`."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from djansin.kasejyan.services.user_deactivate import DeactivateAccountService


@pytest.fixture
def service():
    return DeactivateAccountService()


@pytest.fixture
def user_with_sessions(db, user):
    """A user with three outstanding refresh tokens."""
    tokens = [RefreshToken.for_user(user) for _ in range(3)]
    return user, tokens


class TestDeactivateAccountService:
    def test_deactivates_account_and_revokes_all_sessions(
        self, service, user_with_sessions
    ):
        user, tokens = user_with_sessions

        result = service(
            user=user,
            current_password="secret123",
            reason="No longer needed",
        )

        user.refresh_from_db()
        assert user.is_active is False
        assert result.username == user.username
        assert result.deactivated_at is not None
        assert len(result.revoked_sessions) == 3

    def test_revokes_sessions_even_without_reason(self, service, user_with_sessions):
        user, _ = user_with_sessions

        result = service(user=user, current_password="secret123")

        assert len(result.revoked_sessions) == 3

    def test_rejects_wrong_password(self, service, user):
        with pytest.raises(Exception) as exc:
            service(user=user, current_password="wrong")
        # BusinessRuleViolation → 422
        assert exc.value.error.http_status == 422

        user.refresh_from_db()
        assert user.is_active is True  # unchanged

    def test_rejects_empty_password(self, service, user):
        with pytest.raises(Exception) as exc:
            service(user=user, current_password="")
        # InvalidFormat → 400
        assert exc.value.error.http_status == 422

        user.refresh_from_db()
        assert user.is_active is True

    def test_rejects_already_inactive_account(self, service, user):
        user.is_active = False
        user.save(update_fields=["is_active"])

        with pytest.raises(Exception) as exc:
            service(user=user, current_password="secret123")
        assert exc.value.error.http_status == 422

    def test_does_not_touch_contacts(self, service, user_with_email):
        user = user_with_email

        service(user=user, current_password="secret123")

        user.refresh_from_db()
        assert user.is_active is False
        # Email is retained (soft deactivation)
        assert user.email is not None
        assert user.email.address == "test@example.com"
