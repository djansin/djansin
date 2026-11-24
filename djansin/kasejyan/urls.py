"""URL configuration for the authentication application.

Maps the authentication HTTP endpoints to their corresponding views and
defines the URL namespace ``"auth"`` used for reverse resolution.

Routes are grouped by concern:

* Sign-in / sign-up / refresh / sign-out — open to unauthenticated
  clients, or authenticated by the token itself.
* Session management (list, revoke) — authenticated.
* Password and username changes — authenticated.
* Email and phone changes/removals — two-step flows (request +
  confirm), authenticated.
* Password reset — two-step flow, open to unauthenticated clients.
"""

from django.urls import path

from djansin.kasejyan.views import (
    AuthenticateView,
    ChangeEmailView,
    ChangePasswordView,
    ChangePhoneView,
    ChangeUsernameView,
    ListUserSessionsView,
    PasswordResetView,
    RefreshTokenView,
    RemoveEmailView,
    RemovePhoneView,
    RequestChangeEmailView,
    RequestChangePhoneView,
    RequestPasswordResetView,
    RequestRemoveEmailView,
    RequestRemovePhoneView,
    RevokeSessionView,
    SignoutView,
    VerificationCodeView,
)


# Namespace for URL reversing
app_name = "auth"

urlpatterns = [
    # --- Sign-in / sign-up / verify / refresh / sign-out ---
    path("", AuthenticateView.as_view(), name="sign-in-up"),
    path("verify/", VerificationCodeView.as_view(), name="verify"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("signout/", SignoutView.as_view(), name="signout"),
    # --- Session management ---
    path("sessions/", ListUserSessionsView.as_view(), name="session-list"),
    path("sessions/<str:jti>/", RevokeSessionView.as_view(), name="session-revoke"),
    # --- Password / username ---
    path("me/password/", ChangePasswordView.as_view(), name="password-change"),
    path("me/username/", ChangeUsernameView.as_view(), name="username-change"),
    # --- Phone change (two-step) ---
    path(
        "me/phone/change/request/",
        RequestChangePhoneView.as_view(),
        name="phone-change-request",
    ),
    path("me/phone/change/", ChangePhoneView.as_view(), name="phone-change"),
    # --- Phone removal (two-step) ---
    path(
        "me/phone/remove/request/",
        RequestRemovePhoneView.as_view(),
        name="phone-remove-request",
    ),
    path("me/phone/remove/", RemovePhoneView.as_view(), name="phone-remove"),
    # --- Email change (two-step) ---
    path(
        "me/email/change/request/",
        RequestChangeEmailView.as_view(),
        name="email-change-request",
    ),
    path("me/email/change/", ChangeEmailView.as_view(), name="email-change"),
    # --- Email removal (two-step) ---
    path(
        "me/email/remove/request/",
        RequestRemoveEmailView.as_view(),
        name="email-remove-request",
    ),
    path("me/email/remove/", RemoveEmailView.as_view(), name="email-remove"),
    # --- Password reset (two-step, unauthenticated) ---
    path(
        "password/reset/request/",
        RequestPasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
]
