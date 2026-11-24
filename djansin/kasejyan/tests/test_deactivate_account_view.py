"""Tests for :class:`DeactivateAccountView`."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api(db):
    return APIClient()


@pytest.fixture
def auth_api(api, user):
    token = RefreshToken.for_user(user)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api, user, token


class TestDeactivateAccountView:
    def test_deactivates_account(self, auth_api):
        api, user, _ = auth_api
        url = reverse("auth:user-deactivate")

        resp = api.post(
            url,
            {"current_password": "secret123", "reason": "Testing"},
            format="json",
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == "ACCOUNT_DEACTIVATED"
        assert body["data"]["username"] == user.username
        assert "revoked_sessions" in body["data"]

        user.refresh_from_db()
        assert user.is_active is False

    def test_rejects_wrong_password(self, auth_api):
        api, user, _ = auth_api
        url = reverse("auth:user-deactivate")

        resp = api.post(url, {"current_password": "wrong"}, format="json")

        assert resp.status_code == 422
        assert resp.json()["code"].startswith("BIZ:")

        user.refresh_from_db()
        assert user.is_active is True

    def test_rejects_missing_password(self, auth_api):
        api, _, _ = auth_api
        url = reverse("auth:user-deactivate")

        resp = api.post(url, {}, format="json")

        assert resp.status_code == 422

    def test_rejects_unauthenticated(self, api):
        url = reverse("auth:user-deactivate")
        resp = api.post(url, {"current_password": "secret123"}, format="json")
        assert resp.status_code == 401

    def test_reason_is_optional(self, auth_api):
        api, user, _ = auth_api
        url = reverse("auth:user-deactivate")

        resp = api.post(url, {"current_password": "secret123"}, format="json")

        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.is_active is False

    def test_revokes_sessions(self, auth_api):
        api, user, _ = auth_api
        url = reverse("auth:user-deactivate")

        # Create extra sessions before deactivating
        for _ in range(2):
            RefreshToken.for_user(user)

        resp = api.post(url, {"current_password": "secret123"}, format="json")

        assert resp.status_code == 200
        assert len(resp.json()["data"]["revoked_sessions"]) >= 3
