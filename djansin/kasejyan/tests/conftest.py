import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from djansin.kasejyan.models import Email, Phone


User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="secret123")


@pytest.fixture
def user_with_email(db, user):
    Email.objects.create(address="test@example.com", user=user)
    return user


@pytest.fixture
def user_with_phone(db, user):
    Phone.objects.create(number="+989123456789", user=user)
    return user


@pytest.fixture
def email_contact(db):
    return Email.objects.create(address="target@example.com")


@pytest.fixture
def phone_contact(db):
    return Phone.objects.create(number="+989121234567")


@pytest.fixture
def expired_code(contact, purpose):
    """Issue a code and immediately expire it."""
    contact.refresh_code(purpose=purpose, minutes=1)
    contact.code_expires_at = timezone.now() - timezone.timedelta(seconds=1)
    contact.save(update_fields=["code_expires_at"])
    return contact


@pytest.fixture
def blocked_contact(contact):
    contact.blocked_until = timezone.now() + timezone.timedelta(minutes=10)
    contact.save(update_fields=["blocked_until"])
    return contact


@pytest.fixture
def frozen_time():
    """Freeze time to a known instant for deterministic expiry tests."""
    with freeze_time("2026-01-01 12:00:00") as frozen:
        yield frozen
