from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError
from core.exceptions.errors.business import (
    BusinessRuleViolation,
    ResourceNotFound,
)
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import IssueTokenResult


class RefreshTokenService(Service[IssueTokenResult]):
    """Refreshes an access token using a valid refresh token.

    The service validates the incoming refresh token, ensures the user is
    still active, rotates the refresh token (blacklists the old one and
    issues a new pair), and returns the new credentials.
    """

    def execute(self, refresh_token: str) -> IssueTokenResult:
        token = self._load_token(refresh_token)

        # Rotate: blacklist the old refresh token so it can't be reused.
        try:
            token.blacklist()
        except TokenError as exc:
            # If the token was already blacklisted or otherwise invalid,
            # we still return the freshly issued tokens — but we raise a
            # business error to signal the anomaly to the caller.
            raise BusinessError(
                BusinessRuleViolation(
                    reason=_t("Refresh token has already been revoked.")
                )
            ) from exc

        user = self._resolve_token_user(token)

        new_refresh = RefreshToken.for_user(user)

        return IssueTokenResult(
            user=user,
            refresh=new_refresh,
        )

    def _load_token(self, refresh_token: str) -> RefreshToken:
        if not refresh_token:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Refresh token is required."))
            )

        try:
            return RefreshToken(token=refresh_token)
        except TokenError as exc:
            raise BusinessError(
                BusinessRuleViolation(reason=_t("Invalid or expired refresh token."))
            ) from exc

    def _resolve_token_user(self, token: RefreshToken) -> User:
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
