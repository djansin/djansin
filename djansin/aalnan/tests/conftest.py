import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="secret123")


@pytest.fixture
def api(db):
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def auth_api(api, user):
    from rest_framework_simplejwt.tokens import RefreshToken

    token = RefreshToken.for_user(user)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api, user
