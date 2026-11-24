from .authenticate import AuthenticateView
from .email_change import ChangeEmailView, RequestChangeEmailView
from .email_remove import RemoveEmailView, RequestRemoveEmailView
from .password_change import ChangePasswordView
from .password_reset import PasswordResetView, RequestPasswordResetView
from .phone_change import ChangePhoneView, RequestChangePhoneView
from .phone_remove import RemovePhoneView, RequestRemovePhoneView
from .refresh_token import RefreshTokenView
from .revoke_session import RevokeSessionView
from .signout import SignoutView
from .user_deactivate import DeactivateAccountView
from .user_sessions import ListUserSessionsView
from .username_change import ChangeUsernameView
from .verification_code import VerificationCodeView


__all__: list[str] = [
    "AuthenticateView",
    "ChangeEmailView",
    "RequestChangeEmailView",
    "RemoveEmailView",
    "RequestRemoveEmailView",
    "ChangePasswordView",
    "RequestPasswordResetView",
    "ChangePhoneView",
    "RequestChangePhoneView",
    "RemovePhoneView",
    "RequestRemovePhoneView",
    "PasswordResetView",
    "RefreshTokenView",
    "RevokeSessionView",
    "SignoutView",
    "DeactivateAccountView",
    "ListUserSessionsView",
    "ChangeUsernameView",
    "VerificationCodeView",
]
