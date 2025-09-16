from django.urls import path
from .views import (
    SignupView,
    LoginView,
    LogoutView,
    PasswordResetView,
    SetNewPasswordView,
    ProfileView
)

urlpatterns = [
    # Signup
    path('signup/', SignupView.as_view(), name='signup'),

    # Login
    path('login/', LoginView.as_view(), name='login'),

    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password reset request
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),

    # Set new password (link from email)
    path('reset/<uidb64>/<token>/', SetNewPasswordView.as_view(), name='set_new_password'),

    # Profile (requires login)
    path('profile/', ProfileView.as_view(), name='profile'),
]
