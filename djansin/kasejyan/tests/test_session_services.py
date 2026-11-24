"""Tests for the session management services.

Covers:

* ``ListUserSessionsService`` — active-only listing (revoked and expired
  sessions are excluded).
* ``RevokeSessionService`` — single-session revocation with ownership
  enforcement.
* ``RevokeUserSessionsService`` — bulk revocation with ``exclude_jtis``
  support.
* ``SignoutService`` — refresh-token-based sign-out.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from djansin.kasejyan.services.revoke_session import RevokeSessionService
from djansin.kasejyan.services.revoke_sessions import RevokeUserSessionsService
from djansin.kasejyan.services.signout import SignoutService
from djansin.kasejyan.services.user_sessions import ListUserSessionsService


User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user_with_tokens(db, user):
    """A user with three outstanding refresh tokens."""
    tokens = [RefreshToken.for_user(user) for _ in range(3)]
    return user, tokens


@pytest.fixture
def other_user_with_token(db):
    """A second user with a single refresh token, for ownership tests."""
    other = User.objects.create_user(username="other", password="x")
    token = RefreshToken.for_user(other)
    return other, token


# ---------------------------------------------------------------------------
# ListUserSessionsService
# ---------------------------------------------------------------------------


class TestListUserSessionsService:
    """Tests for listing a user's active sessions."""

    @pytest.fixture
    def service(self):
        return ListUserSessionsService()

    def test_lists_active_sessions_only(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        revoked_jti = tokens[0]["jti"]
        tokens[0].blacklist()

        result = service(identifier=user.username)

        assert len(result) == 2
        assert all(s.jti != revoked_jti for s in result)

    def test_matches_active_set_in_database(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        tokens[0].blacklist()

        result = service(identifier=user.username)

        expected_jtis = set(
            OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now())
            .exclude(id__in=BlacklistedToken.objects.values("token_id"))
            .values_list("jti", flat=True)
        )
        assert {s.jti for s in result} == expected_jtis

    def test_excludes_expired_sessions(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        expired_jti = tokens[0]["jti"]
        OutstandingToken.objects.filter(jti=expired_jti).update(
            expires_at=timezone.now() - timezone.timedelta(seconds=1)
        )

        result = service(identifier=user.username)

        assert len(result) == 2
        assert all(s.jti != expired_jti for s in result)

    def test_returns_empty_for_user_without_sessions(self, service, user):
        result = service(identifier=user.username)
        assert result == []

    def test_orders_newest_first(self, service, user_with_tokens):
        user, tokens = user_with_tokens

        result = service(identifier=user.username)

        created_ats = [s.created_at for s in result]
        assert created_ats == sorted(created_ats, reverse=True)

    def test_raises_for_unknown_user(self, service, db):
        with pytest.raises(Exception):
            service(identifier="does-not-exist")


# ---------------------------------------------------------------------------
# RevokeSessionService
# ---------------------------------------------------------------------------


class TestRevokeSessionService:
    """Tests for revoking a single session by ``jti``."""

    @pytest.fixture
    def service(self):
        return RevokeSessionService()

    def test_revokes_own_session(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        jti = tokens[0]["jti"]

        result = service(jti=jti, user=user)

        assert result.jti == jti
        assert result.username == user.username
        assert BlacklistedToken.objects.filter(token__jti=jti).exists()

    def test_returns_blacklisted_at(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        jti = tokens[0]["jti"]

        result = service(jti=jti, user=user)

        blacklisted = BlacklistedToken.objects.get(token__jti=jti)
        assert result.revoked_at == blacklisted.blacklisted_at

    def test_rejects_already_revoked(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        jti = tokens[0]["jti"]
        service(jti=jti, user=user)

        with pytest.raises(Exception):
            service(jti=jti, user=user)

    def test_rejects_expired_session(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        jti = tokens[0]["jti"]
        OutstandingToken.objects.filter(jti=jti).update(
            expires_at=timezone.now() - timezone.timedelta(seconds=1)
        )

        with pytest.raises(Exception):
            service(jti=jti, user=user)

    def test_rejects_other_users_session(
        self, service, user_with_tokens, other_user_with_token
    ):
        user, _ = user_with_tokens
        _, other_token = other_user_with_token

        with pytest.raises(Exception):
            service(jti=other_token["jti"], user=user)

    def test_rejects_empty_jti(self, service, user):
        with pytest.raises(Exception):
            service(jti="", user=user)


# ---------------------------------------------------------------------------
# RevokeUserSessionsService
# ---------------------------------------------------------------------------


class TestRevokeUserSessionsService:
    """Tests for revoking every session of a user."""

    @pytest.fixture
    def service(self):
        return RevokeUserSessionsService()

    def test_revokes_all_sessions(self, service, user_with_tokens):
        user, _ = user_with_tokens

        result = service(identifier=user.username)

        assert len(result) == 3
        assert BlacklistedToken.objects.filter(token__user=user).count() == 3

    def test_excludes_given_jtis(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        keep_jti = tokens[0]["jti"]

        result = service(identifier=user.username, exclude_jtis={keep_jti})

        assert len(result) == 2
        assert not BlacklistedToken.objects.filter(token__jti=keep_jti).exists()
        assert all(s.jti != keep_jti for s in result)

    def test_skips_already_revoked(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        tokens[0].blacklist()

        result = service(identifier=user.username)

        assert len(result) == 2
        assert all(s.jti != tokens[0]["jti"] for s in result)

    def test_returns_empty_for_user_without_sessions(self, service, user):
        result = service(identifier=user.username)
        assert result == []

    def test_raises_for_unknown_user(self, service, db):
        with pytest.raises(Exception):
            service(identifier="does-not-exist")


# ---------------------------------------------------------------------------
# SignoutService
# ---------------------------------------------------------------------------


class TestSignoutService:
    """Tests for refresh-token-based sign-out."""

    @pytest.fixture
    def service(self):
        return SignoutService()

    def test_signs_out_by_refresh_token(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        raw = str(tokens[0])

        result = service(refresh_token=raw, user=user)

        assert result.jti == tokens[0]["jti"]
        assert BlacklistedToken.objects.filter(token__jti=tokens[0]["jti"]).exists()

    def test_signs_out_without_user_scope(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        raw = str(tokens[0])

        result = service(refresh_token=raw)

        assert result.jti == tokens[0]["jti"]

    def test_rejects_other_users_token(
        self, service, user_with_tokens, other_user_with_token
    ):
        user, _ = user_with_tokens
        _, other_token = other_user_with_token

        with pytest.raises(Exception):
            service(refresh_token=str(other_token), user=user)

    def test_rejects_already_revoked_token(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        raw = str(tokens[0])
        service(refresh_token=raw, user=user)

        with pytest.raises(Exception):
            service(refresh_token=raw, user=user)

    def test_rejects_invalid_token(self, service, user):
        with pytest.raises(Exception):
            service(refresh_token="not-a-jwt", user=user)

    def test_rejects_empty_token(self, service, user):
        with pytest.raises(Exception):
            service(refresh_token="", user=user)

    def test_rejects_expired_session(self, service, user_with_tokens):
        user, tokens = user_with_tokens
        jti = tokens[0]["jti"]
        OutstandingToken.objects.filter(jti=jti).update(
            expires_at=timezone.now() - timezone.timedelta(seconds=1)
        )

        with pytest.raises(Exception):
            service(refresh_token=str(tokens[0]), user=user)
