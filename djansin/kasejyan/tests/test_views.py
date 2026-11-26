import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def auth_api(api, user):
    token = RefreshToken.for_user(user)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api, user, token


class TestAuthenticateView:
    def test_login_with_password(self, api, user):
        url = reverse("kasejyan:sign-in-up")
        resp = api.post(
            url,
            {
                "identifier": user.username,
                "password": "secret123",
                "password_confirm": "secret123",
            },
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == "AUTH_TOKEN_ISSUED"
        assert "access" in resp.json()["data"]

    def test_rejects_invalid_payload(self, api):
        url = reverse("kasejyan:sign-in-up")
        resp = api.post(url, {}, format="json")
        assert resp.status_code == 422


class TestRefreshTokenView:
    def test_refreshes_token(self, api, user):
        refresh = str(RefreshToken.for_user(user))
        url = reverse("kasejyan:refresh")

        resp = api.post(url, {"refresh_token": refresh}, format="json")

        assert resp.status_code == 200
        assert resp.json()["code"] == "AUTH_TOKEN_REFRESHED"

    def test_rejects_invalid_token(self, api):
        url = reverse("kasejyan:refresh")
        resp = api.post(url, {"refresh_token": "invalid"}, format="json")
        assert resp.status_code == 422


class TestSignoutView:
    def test_signs_out_single_device(self, auth_api):
        api, user, token = auth_api
        url = reverse("kasejyan:signout")
        resp = api.post(
            url,
            {"all_devices": False, "refresh": str(token)},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == "SESSION_REVOKED"

    def test_signs_out_all_devices(self, auth_api):
        api, user, token = auth_api
        url = reverse("kasejyan:signout")
        resp = api.post(url, {"all_devices": True}, format="json")
        assert resp.status_code == 200
        assert resp.json()["code"] == "ALL_SESSIONS_REVOKED"


class TestChangePasswordView:
    def test_changes_password(self, auth_api):
        api, user, token = auth_api
        url = reverse("kasejyan:password-change")
        resp = api.post(
            url,
            {
                "current_password": "secret123",
                "new_password": "newsecret456",
                "new_password_confirm": "newsecret456",
                "refresh_token": str(token),
            },
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == "PASSWORD_CHANGED"


class TestListUserSessionsView:
    def test_lists_sessions(self, auth_api):
        api, user, _ = auth_api
        url = reverse("kasejyan:session-list")
        resp = api.get(url)
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)


class TestRevokeSessionView:
    def test_revokes_own_session(self, auth_api):
        api, user, token = auth_api
        jti = token["jti"]
        url = reverse("kasejyan:session-revoke", kwargs={"jti": jti})
        resp = api.delete(url)
        assert resp.status_code == 200
        assert resp.json()["code"] == "SESSION_REVOKED"
