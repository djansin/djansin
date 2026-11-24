import pytest
from django.utils import timezone

from djansin.kasejyan.models.email import Email
from djansin.kasejyan.models.mixins.verifiable import CodePurpose
from djansin.kasejyan.services.email_change import ChangeEmailService
from djansin.kasejyan.services.email_change_request import RequestChangeEmailService


class TestRequestChangeEmailService:
    @pytest.fixture
    def service(self):
        return RequestChangeEmailService()

    def test_dispatches_code_to_new_email(self, service, user):
        result = service(user=user, new_email="new@example.com")
        assert result.new_email == "new@example.com"

    def test_returns_generic_result_for_blocked_email(self, service, user):
        from djansin.kasejyan.models import Email

        contact = Email.objects.create(address="blocked@example.com")
        contact.blocked_until = timezone.now() + timezone.timedelta(minutes=10)
        contact.save(update_fields=["blocked_until"])

        result = service(user=user, new_email="blocked@example.com")
        assert result.new_email == "blocked@example.com"
        assert result.expires_at is not None


class TestChangeEmailService:
    @pytest.fixture
    def service(self):
        return ChangeEmailService()

    def test_changes_email(self, service, user_with_email):
        new_contact = Email.objects.create(address="new@example.com")
        code = new_contact.refresh_code(purpose=CodePurpose.CHANGE_CONTACT)

        result = service(user=user_with_email, new_email="new@example.com", code=code)

        user_with_email.refresh_from_db()
        assert user_with_email.email.address == "new@example.com"
        assert result.old_email == "test@example.com"

    def test_rejects_wrong_purpose(self, service, user_with_email, email_contact):
        code = email_contact.refresh_code(purpose=CodePurpose.REMOVE_CONTACT)

        with pytest.raises(Exception):
            service(user=user_with_email, new_email=str(email_contact), code=code)

    def test_rejects_email_owned_by_other(self, service, user_with_email, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        other = User.objects.create_user(username="other", password="x")
        Email.objects.create(address="other@example.com", user=other)

        contact = Email.objects.get(address="other@example.com")
        code = contact.refresh_code(purpose=CodePurpose.CHANGE_CONTACT)

        with pytest.raises(Exception):
            service(user=user_with_email, new_email="other@example.com", code=code)
