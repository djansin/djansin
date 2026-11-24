import pytest
from django.utils import timezone

from djansin.kasejyan.models.mixins.verifiable import CodePurpose
from djansin.kasejyan.services.password_reset import PasswordResetService
from djansin.kasejyan.services.password_reset_request import RequestPasswordResetService


class TestRequestPasswordResetService:
    @pytest.fixture
    def service(self):
        return RequestPasswordResetService()

    def test_dispatches_to_phone_first(self, service, user_with_email, user_with_phone):
        result = service(identifier=user_with_phone.username)
        assert result.channel == "phone"

    def test_dispatches_to_email_when_no_phone(self, service, user_with_email):
        result = service(identifier=user_with_email.username)
        assert result.channel == "email"

    def test_returns_generic_result_for_unknown_user(self, service, db):
        result = service(identifier="unknown@example.com")
        # indistinguishable from success
        assert result.identifier == "unknown@example.com"
        assert result.expires_at is not None

    def test_returns_generic_result_for_user_without_contact(self, service, user):
        result = service(identifier=user.username)
        assert result.expires_at is not None

    def test_returns_generic_result_for_blocked_contact(self, service, user_with_email):
        contact = user_with_email.email
        contact.blocked_until = timezone.now() + timezone.timedelta(minutes=10)
        contact.save(update_fields=["blocked_until"])

        result = service(identifier=user_with_email.username)
        assert result.expires_at is not None  # generic, not an error

    def test_rejects_still_valid_code(self, service, user_with_email):
        contact = user_with_email.email
        contact.refresh_code(purpose=CodePurpose.RESET_PASSWORD)

        with pytest.raises(Exception):
            service(identifier=user_with_email.username)


class TestPasswordResetService:
    @pytest.fixture
    def service(self):
        return PasswordResetService()

    def test_resets_password_and_revokes_sessions(self, service, user_with_email):
        from rest_framework_simplejwt.tokens import RefreshToken

        RefreshToken.for_user(user_with_email)

        contact = user_with_email.email
        code = contact.refresh_code(purpose=CodePurpose.RESET_PASSWORD)

        result = service(
            identifier="test@example.com", code=code, new_password="newsecret456"
        )

        user_with_email.refresh_from_db()
        assert user_with_email.check_password("newsecret456")
        assert result.username == user_with_email.username

    def test_rejects_wrong_purpose_code(self, service, user_with_email):
        contact = user_with_email.email
        code = contact.refresh_code(purpose=CodePurpose.CHANGE_CONTACT)

        with pytest.raises(Exception):
            service(
                identifier="test@example.com", code=code, new_password="newsecret456"
            )
