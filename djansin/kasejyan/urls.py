"""URL configuration for the authentication application.

This module maps the authentication HTTP endpoints to their corresponding
views and defines the URL namespace ``"auth"`` used for reverse resolution.
Two routes are exposed: one for requesting a one-time verification code
and one for signing in or registering a user.
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
    path("", AuthenticateView.as_view(), name="sign-in-up"),
    path("verify/", VerificationCodeView.as_view(), name="verify"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("signout/", SignoutView.as_view(), name="signout"),
    path("sessions/", ListUserSessionsView.as_view(), name="sessions"),
    path("sessions/<str:jti>/", RevokeSessionView.as_view(), name="revoke"),
    path("me/password/", ChangePasswordView.as_view(), name="password-change"),
    path("me/username/", ChangeUsernameView.as_view(), name="username-change"),
    path(
        "me/phone/change/request/",
        RequestChangePhoneView.as_view(),
        name="phone-change-request",
    ),
    path("me/phone/change/", ChangePhoneView.as_view(), name="phone-change"),
    path(
        "me/phone/remove/request/",
        RequestRemovePhoneView.as_view(),
        name="phone-remove-request",
    ),
    path("me/phone/remove/", RemovePhoneView.as_view(), name="phone-remove"),
    path(
        "me/email/change/request/",
        RequestChangeEmailView.as_view(),
        name="email-change-request",
    ),
    path("me/email/change/", ChangeEmailView.as_view(), name="email-change"),
    path(
        "me/email/remove/request/",
        RequestRemoveEmailView.as_view(),
        name="email-remove-request",
    ),
    path("me/email/remove/", RemoveEmailView.as_view(), name="email-remove"),
    path(
        "password/reset/request/",
        RequestPasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
]
