"""Typed result object for issued authentication tokens.

This module defines :class:`IssueTokenResult`, a lightweight dataclass
that bundles an authenticated user with the refresh token issued for that
user. It provides a serialization helper that renders the token pair,
expiration metadata, and the public user representation into a plain
dictionary suitable for API responses.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from core.types import Result
from djansin.kasejyan.models import User
from djansin.kasejyan.serializers.user import UserSerializer


@dataclass(frozen=True, slots=True)
class IssueTokenResult(Result):
    """Container for an issued refresh/access token pair and its subject.

    Pairs the authenticated :class:`~djansin.kasejyan.models.User` with
    the :class:`~rest_framework_simplejwt.tokens.RefreshToken` generated for
    it, and exposes :meth:`to_dict` to render a serializable
    representation including token strings, expiration timestamps, and
    remaining lifetimes.

    Attributes:
        user (User): The authenticated user the tokens were issued for.
        refresh (RefreshToken): The refresh token issued for ``user``; its
            access token is derived lazily.
        token_type (str): Authorization scheme label used in responses.
            Defaults to ``"Bearer"``.
    """

    user: User
    refresh: RefreshToken
    token_type: str = "Bearer"

    def to_dict(self) -> dict[str, Any]:
        """Render the issued tokens and metadata as a plain dictionary.

        Produces a payload containing the token type, the string forms of
        the refresh and access tokens, their absolute expiration
        timestamps, their remaining lifetimes in seconds, and the
        serialized public user representation.

        Returns:
            dict[str, Any]: A dictionary with keys ``token_type``,
            ``refresh``, ``access``, ``access_expires_at``,
            ``refresh_expires_at``, ``access_expires_in``,
            ``refresh_expires_in``, and ``user``.
        """
        access_token = self.refresh.access_token

        now = timezone.now()

        access_exp_timestamp = access_token.payload.get("exp")
        refresh_exp_timestamp = self.refresh.payload.get("exp")

        # Convert timestamps to datetime
        access_expires_at: datetime = timezone.make_aware(
            datetime.fromtimestamp(access_exp_timestamp)
        )
        refresh_expires_at: datetime = timezone.make_aware(
            datetime.fromtimestamp(refresh_exp_timestamp)
        )

        access_expires_in = int((access_expires_at - now).total_seconds())
        refresh_expires_in = int((refresh_expires_at - now).total_seconds())

        return {
            "token_type": self.token_type,
            "refresh": str(self.refresh),
            "access": str(access_token),
            "access_expires_at": access_expires_at,
            "refresh_expires_at": refresh_expires_at,
            "access_expires_in": access_expires_in,
            "refresh_expires_in": refresh_expires_in,
            "user": UserSerializer(self.user).data,
        }


@dataclass(frozen=True, slots=True)
class CodeDispatchResult(Result):
    type: str
    identifier: str


@dataclass(frozen=True, slots=True)
class RegisteredUser(Result):
    pk: int
    uuid: str
    username: str
    email: str | None
    phone: str | None
    is_active: bool
    is_staff: bool
    is_superuser: bool
    date_joined: datetime


@dataclass(frozen=True, slots=True)
class RevokedSessionResult(Result):
    """Information about a single revoked JWT session.

    Attributes:
        jti (str): The unique JWT ID of the revoked session.
        username (str | None): Username of the session owner, if known.
        created_at (datetime | None): When the session's refresh token was
            originally issued.
        expires_at (datetime | None): When the refresh token would have
            expired.
        revoked_at (datetime): When the blacklist entry was created (i.e.
            the moment of revocation).
    """

    jti: str
    username: str | None
    created_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime

    def get_created_at(self, value: datetime) -> datetime:
        return value.isoformat()

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()

    def get_revoked_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class UserSessionResult(Result):
    """A single session (refresh token) belonging to a user."""

    jti: str
    username: str
    created_at: datetime
    expires_at: datetime

    def get_created_at(self, value: datetime) -> datetime:
        return value.isoformat()

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PasswordChangeResult(Result):
    """Outcome of a successful password change."""

    username: str
    changed_at: datetime
    revoked_sessions: list[RevokedSessionResult]

    def get_changed_at(self, value: datetime) -> datetime:
        return value.isoformat()

    def get_revoked_sessions(self, value: list[RevokedSessionResult]) -> list[dict]:
        return [s.to_dict() for s in value]


@dataclass(frozen=True, slots=True)
class PasswordResetRequestResult(Result):
    """Outcome of a password-reset code request."""

    channel: str
    identifier: str
    expires_at: datetime

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PasswordResetResult(Result):
    """Outcome of a successful password reset."""

    username: str
    changed_at: datetime

    def get_changed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class VerifiedContactResult(Result):
    """Outcome of a successful verification.

    Carries the verified contact's identity and, when the contact is
    already linked to an account, the associated user. Consumers can
    use ``user`` directly instead of re-resolving the identifier.
    """

    contact_type: str
    identifier: str
    user: User | None
    is_newly_verified: bool


@dataclass(frozen=True, slots=True)
class UsernameChangeResult(Result):
    """Outcome of a successful username change."""

    old_username: str
    new_username: str
    changed_at: datetime

    def get_changed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class EmailRemovalResult(Result):
    """Outcome of a successful email removal."""

    username: str
    removed_email: str
    removed_at: datetime

    def get_removed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class EmailRemovalRequestResult(Result):
    """Outcome of an email-removal code request."""

    email: str
    expires_at: datetime

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PhoneRemovalResult(Result):
    """Outcome of a successful phone removal."""

    username: str
    removed_phone: str
    removed_at: datetime

    def get_removed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PhoneRemovalRequestResult(Result):
    """Outcome of a phone-removal code request."""

    phone: str
    expires_at: datetime

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class EmailChangeResult(Result):
    """Outcome of a successful email change."""

    username: str
    old_email: str | None
    new_email: str
    changed_at: datetime

    def get_changed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class EmailChangeRequestResult(Result):
    """Outcome of an email-change code request."""

    new_email: str
    expires_at: datetime

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PhoneChangeResult(Result):
    """Outcome of a successful phone change."""

    username: str
    old_phone: str | None
    new_phone: str
    changed_at: datetime

    def get_changed_at(self, value: datetime) -> datetime:
        return value.isoformat()


@dataclass(frozen=True, slots=True)
class PhoneChangeRequestResult(Result):
    """Outcome of a phone-change code request."""

    new_phone: str
    expires_at: datetime

    def get_expires_at(self, value: datetime) -> datetime:
        return value.isoformat()
