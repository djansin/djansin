from django.utils import timezone
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import BusinessError
from core.exceptions.errors.business import ResourceNotFound
from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import RevokedSessionResult


class SignoutService(Service[RevokedSessionResult]):
    def execute(self, refresh_token: str, user: User | None = None) -> RevokedSessionResult:
        qs = OutstandingToken.objects.filter(token=refresh_token)
        if user is not None:
            qs = qs.filter(user=user)

        token_obj = qs.first()
        if token_obj is None:
            raise BusinessError(ResourceNotFound(resource=_t("Session")))

        if BlacklistedToken.objects.filter(token=token_obj).exists():
            raise BusinessError(ResourceNotFound(resource=_t("Session")))

        RefreshToken(token=token_obj.token).blacklist()

        return RevokedSessionResult(
            jti=token_obj.jti,
            username=token_obj.user.username,
            created_at=token_obj.created_at,
            expires_at=token_obj.expires_at,
            revoked_at=timezone.now(),
        )
