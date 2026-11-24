import pytest

from djansin.kasejyan.exceptions import InvalidLoginIdentifier
from djansin.kasejyan.models.mixins.verifiable import CodePurpose
from djansin.kasejyan.services.authenticate import AuthenticateService


@pytest.fixture
def service():
    return AuthenticateService()


class TestAuthenticateService:
    def test_login_by_username_with_password(self, service, user):
        result = service(identifier="testuser", password="secret123")
        assert result.pk == user.pk

    def test_login_by_username_wrong_password(self, service, user):
        with pytest.raises(Exception) as exc:
            service(identifier="testuser", password="wrong")
        assert isinstance(exc.value.error, InvalidLoginIdentifier)

    def test_register_by_username(self, service, db):
        result = service(identifier="newuser", password="secret123")
        assert result.username == "newuser"

    def test_login_by_email_with_password(self, service, user_with_email):
        result = service(identifier="test@example.com", password="secret123")
        assert result.pk == user_with_email.pk

    def test_login_by_phone_with_password(self, service, user_with_phone):
        result = service(identifier="+989123456789", password="secret123")
        assert result.pk == user_with_phone.pk

    def test_login_by_email_with_valid_code(self, service, user_with_email):
        contact = user_with_email.email
        code = contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)

        result = service(identifier="test@example.com", code=code)
        assert result.pk == user_with_email.pk

    def test_rejects_code_for_wrong_purpose(self, service, user_with_email):
        contact = user_with_email.email
        code = contact.refresh_code(purpose=CodePurpose.RESET_PASSWORD)

        with pytest.raises(Exception) as exc:
            service(identifier="test@example.com", code=code)
        assert isinstance(exc.value.error, InvalidLoginIdentifier)

    def test_rejects_both_password_and_code(self, service, user):
        with pytest.raises(Exception) as exc:
            service(identifier="testuser", password="secret123", code="123456")
        assert isinstance(exc.value.error, InvalidLoginIdentifier)

    def test_rejects_invalid_identifier_format(self, service):
        with pytest.raises(Exception):
            service(identifier="not valid!", password="secret123")

    def test_provisions_user_on_first_code_login(self, service, email_contact):
        code = email_contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)

        result = service(identifier=str(email_contact), code=code)

        assert result.username  # generated
        email_contact.refresh_from_db()
        assert email_contact.user_id is not None
