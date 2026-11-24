import pytest
from django.utils import timezone

from djansin.kasejyan.exceptions import InvalidVerificationCode
from djansin.kasejyan.models import Email, Phone
from djansin.kasejyan.models.mixins.verifiable import MAX_ATTEMPTS, VerifiableMixin
from djansin.kasejyan.services.verify_contact import VerifyContactService


CodePurpose = VerifiableMixin.CodePurpose


@pytest.fixture
def service():
    return VerifyContactService()


@pytest.mark.django_db
class TestVerifyContactService:
    @pytest.mark.parametrize(
        "model,identifier_field,identifier",
        [
            (Email, "address", "user@example.com"),
            (Phone, "number", "+989123456789"),
        ],
    )
    def test_verifies_valid_code_for_matching_purpose(
        self, service, model, identifier_field, identifier
    ):
        contact = model.objects.create(**{identifier_field: identifier})
        code = contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)

        result = service(
            identifier=identifier, code=code, purpose=CodePurpose.AUTHENTICATE
        )

        assert result.identifier == str(contact)
        assert result.contact_type == contact.get_model_name()
        assert result.is_newly_verified is True

        contact.refresh_from_db()
        assert contact.is_verified
        assert contact.is_expired  # code invalidated on success

    def test_rejects_wrong_purpose(self, service, email_contact):
        code = email_contact.refresh_code(purpose=CodePurpose.CHANGE_CONTACT)

        with pytest.raises(Exception) as exc:
            service(
                identifier=str(email_contact),
                code=code,
                purpose=CodePurpose.REMOVE_CONTACT,
            )

        assert isinstance(exc.value.error, InvalidVerificationCode)

        email_contact.refresh_from_db()
        assert email_contact.attempts == 0  # wrong purpose doesn't consume attempt

    def test_rejects_expired_code(self, service, email_contact, frozen_time):
        code = email_contact.refresh_code(purpose=CodePurpose.AUTHENTICATE, minutes=1)
        frozen_time.tick(delta=timezone.timedelta(minutes=2))

        with pytest.raises(Exception) as exc:
            service(
                identifier=str(email_contact),
                code=code,
                purpose=CodePurpose.AUTHENTICATE,
            )

        assert isinstance(exc.value.error, InvalidVerificationCode)

    def test_consumes_attempt_on_wrong_code(self, service, email_contact):
        email_contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)

        with pytest.raises(Exception):
            service(
                identifier=str(email_contact),
                code="000000",
                purpose=CodePurpose.AUTHENTICATE,
            )

        email_contact.refresh_from_db()
        assert email_contact.attempts == 1

    def test_rejects_after_max_attempts(self, service, email_contact):
        email_contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)
        email_contact.code_use_attempts = MAX_ATTEMPTS
        email_contact.save(update_fields=["code_use_attempts"])

        with pytest.raises(Exception) as exc:
            service(
                identifier=str(email_contact),
                code="000000",
                purpose=CodePurpose.AUTHENTICATE,
            )

        assert isinstance(exc.value.error, InvalidVerificationCode)

    def test_rejects_blocked_contact(self, service, email_contact):
        code = email_contact.refresh_code(purpose=CodePurpose.AUTHENTICATE)
        email_contact.blocked_until = timezone.now() + timezone.timedelta(minutes=10)
        email_contact.save(update_fields=["blocked_until"])

        with pytest.raises(Exception) as exc:
            service(
                identifier=str(email_contact),
                code=code,
                purpose=CodePurpose.AUTHENTICATE,
            )

        assert isinstance(exc.value.error, InvalidVerificationCode)

    def test_rejects_unknown_identifier(self, service):
        with pytest.raises(Exception) as exc:
            service(
                identifier="unknown@example.com",
                code="123456",
                purpose=CodePurpose.AUTHENTICATE,
            )
        assert isinstance(exc.value.error, InvalidVerificationCode)

    def test_rejects_malformed_identifier(self, service):
        with pytest.raises(Exception) as exc:
            service(
                identifier="not-an-email",
                code="123456",
                purpose=CodePurpose.AUTHENTICATE,
            )
        assert isinstance(exc.value.error, InvalidVerificationCode)
