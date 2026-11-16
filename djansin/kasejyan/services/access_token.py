from rest_framework_simplejwt.tokens import RefreshToken

from core.services import Service
from djansin.kasejyan.models import User
from djansin.kasejyan.types import IssueTokenResult, RegisteredUser


class AccessTokenService(Service[IssueTokenResult]):
    def execute(self, registered_user: RegisteredUser) -> IssueTokenResult:
        user = User.objects.get(pk=registered_user.pk)
        refresh = RefreshToken.for_user(user)
        return IssueTokenResult(user=user, refresh=refresh)
