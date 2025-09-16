# jobsboard/users/urls.py
from django.urls import path
from .views import (
    SignUpAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetRequestAPIView,
    SetNewPasswordAPIView,
    ProfileAPIView,
    users_home,
)

urlpatterns = [
    path("", users_home, name="api-users-home"),
    # Signup
    path("signup/", SignUpAPIView.as_view(), name="api-signup"),
    # Login
    path("login/", LoginAPIView.as_view(), name="api-login"),
    # Logout
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    # Password reset request
    path(
        "password-reset/",
        PasswordResetRequestAPIView.as_view(),
        name="api-password-reset",
    ),
    # Set new password (link from email)
    path(
        "reset/<uidb64>/<token>/",
        SetNewPasswordAPIView.as_view(),
        name="api-set-new-password",
    ),
    # Profile (requires login)
    path("profile/", ProfileAPIView.as_view(), name="api-profile"),
]
