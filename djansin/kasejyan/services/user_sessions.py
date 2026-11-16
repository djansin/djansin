from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from core.exceptions import BusinessError
from core.exceptions.errors.business import ResourceNotFound
from core.services import Service
from djansin.kasejyan.services.mixins import UserResolverMixin
from djansin.kasejyan.types import UserSessionResult


class ListUserSessionsService(UserResolverMixin, Service[list[UserSessionResult]]):
    """List all active sessions (refresh tokens) belonging to a user.

    Resolves the user from an email, phone number, or username, then
    returns every outstanding refresh token issued to that user that is
    still usable — i.e. neither revoked (blacklisted) nor expired. Since
    only active sessions are returned, ``is_revoked`` is always ``False``
    and ``revoked_at`` is always ``None``.
    """

    def execute(self, identifier: str) -> list[UserSessionResult]:
        user = self._resolve_user(identifier)

        if user is None:
            raise BusinessError(ResourceNotFound(resource=_t("User")))

        now = timezone.now()

        token_objs = list(
            OutstandingToken.objects.filter(user=user, expires_at__gt=now)
            .annotate(
                is_revoked=Exists(
                    BlacklistedToken.objects.filter(token_id=OuterRef("id"))
                )
            )
            .filter(is_revoked=False)
            .only("jti", "created_at", "expires_at", "user__username")
            .order_by("-created_at")
        )

        return [
            UserSessionResult(
                jti=token_obj.jti,
                username=token_obj.user.username,
                created_at=token_obj.created_at,
                expires_at=token_obj.expires_at,
            )
            for token_obj in token_objs
        ]
