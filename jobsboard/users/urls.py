#jobboard/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsersViewSet,
    UserFileViewSet,
    SignUpAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetRequestAPIView,
    SetNewPasswordAPIView,
    ProfileAPIView,
    users_home,
)

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='user')        # Admin-only list
router.register(r'files', UserFileViewSet, basename='userfile') # User files CRUD

urlpatterns = [
    # Root informational endpoint
    path("", users_home, name="api-users-home"),

    # Auth & Profile endpoints
    path("signup/", SignUpAPIView.as_view(), name="api-signup"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="api-password-reset"),
    path("reset/<uidb64>/<token>/", SetNewPasswordAPIView.as_view(), name="api-set-new-password"),
    path("profile/", ProfileAPIView.as_view(), name="api-profile"),

    # Router endpoints for ViewSets (keep last to avoid conflicts)
    path("", include(router.urls)),
]
