"""Service layer for refreshing an access token.

Exposes :class:`RefreshTokenService`, which validates an incoming
refresh token, ensures the associated user is still active, rotates the
token (blacklisting the old one and issuing a new pair), and returns the
new credentials.

Rotation order matters: the user is resolved and checked for active
status **before** the old token is blacklisted. If the user is inactive
or missing, the old token is left untouched — otherwise a user whose
account is reactivated later would find themselves logged out with no
way to recover the session.

The service does not consult contact records, so ``CodePurpose`` and
block state are irrelevant here: authentication is carried entirely by
the refresh token, and the only state consulted is the user's active
flag.
"""

from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError, ValidationError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import IssueTokenResult


class RefreshTokenService(Service[IssueTokenResult]):
    """Refresh an access token using a valid refresh token.

    Validates the incoming refresh token, ensures the associated user
    is still active, rotates the token (blacklisting the old one and
    issuing a new pair), and returns the new credentials.

    The old token is blacklisted **after** the user has been resolved
    and confirmed active, so a failed refresh (e.g. deactivated user)
    does not consume the token — the user can retry once the account is
    reactivated.
    """

    def execute(self, refresh_token: str) -> IssueTokenResult:
        """Refresh an access token.

        Args:
            refresh_token (str): The refresh token to rotate.

        Returns:
            IssueTokenResult: The user and the newly issued refresh
            token (from which the access token is derived).

        Raises:
            BusinessError: If the token is missing, invalid, expired,
                already revoked, refers to a missing or inactive user,
                or lacks a user identifier.
            ValidationError: If ``refresh_token`` is empty.
        """
        token = self._load_token(refresh_token)
        user = self._resolve_token_user(token)

        # Rotate only after the user has been confirmed active, so a
        # failed refresh does not consume the token.
        self._blacklist_token(token)

        new_refresh = RefreshToken.for_user(user)

        return IssueTokenResult(
            user=user,
            refresh=new_refresh,
        )

    def _load_token(self, refresh_token: str) -> RefreshToken:
        """Load and structurally validate the refresh token.

        Args:
            refresh_token (str): The raw refresh token string.

        Returns:
            RefreshToken: The parsed token.

        Raises:
            ValidationError: If ``refresh_token`` is empty.
            BusinessError: If the token is malformed, expired, or
                otherwise rejected by SimpleJWT.
        """
        if not refresh_token:
            raise ValidationError(
                InvalidFormat(expected_format=_t("a valid refresh token."))
            )

        try:
            return RefreshToken(token=refresh_token)
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Invalid or expired refresh token."))
            ) from exc

    def _resolve_token_user(self, token: RefreshToken) -> User:
        """Resolve the user referenced by the token and ensure they are active.

        The ``user_id`` claim is the user's primary key, as issued by
        :meth:`RefreshToken.for_user`. The lookup is scoped to the
        primary key, not the public ``uuid`` — refresh tokens are
        internal credentials and never expose public identifiers.

        Args:
            token (RefreshToken): The parsed refresh token.

        Returns:
            User: The active user the token belongs to.

        Raises:
            BusinessError: If the token has no ``user_id`` claim, the
                user no longer exists, or the user is inactive.
        """
        user_id = token.get("user_id")
        if user_id is None:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Refresh token is missing the user identifier.")
                )
            )

        user = User.objects.filter(pk=user_id).first()
        if user is None:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        if not user.is_active:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("User account is not active."))
            )

        return user

    def _blacklist_token(self, token: RefreshToken) -> None:
        """Blacklist the old refresh token.

        Called **after** the user has been resolved and confirmed
        active, so a failed refresh does not consume the token.

        Args:
            token (RefreshToken): The token to blacklist.

        Raises:
            BusinessError: If the token cannot be blacklisted (e.g. it
                was already revoked by a concurrent request).
        """
        try:
            token.blacklist()
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Refresh token has already been revoked.")
                )
            ) from exc
