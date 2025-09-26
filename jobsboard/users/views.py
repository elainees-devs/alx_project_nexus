# jobsboard/users/views.py
import logging
from django.http import JsonResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .models import UserFile
from .serializers import (
    UserSerializer, ProfileSerializer, UserFileSerializer,
    SignUpSerializer, LoginSerializer,
    PasswordResetRequestSerializer, SetNewPasswordSerializer
)
from rate_limit.services import check_rate_limit, RateLimitExceeded

logger = logging.getLogger(__name__)
User = get_user_model()


# -------------------------
# Home Views
# -------------------------
def home(request):
    return JsonResponse({
        "message": "Welcome to the JobsBoard API",
        "instructions": "Use /swagger to access swagger documentation."
    })


def users_home(request):
    return JsonResponse({
        "message": "Welcome to the Users API",
        "endpoints": {
            "auth/signup": "/api/users/signup/",
            "auth/login": "/api/users/auth/login/",
            "auth/logout": "/api/users/auth/logout/",
            "auth/password-reset": "/api/users/auth/password-reset/",
            "auth/reset/<uidb64>/<token>/": "/api/users/auth/reset/<uidb64>/<token>/",
            "profile": "/api/users/profile/"
        }
    })

class AuthViewSet(viewsets.ViewSet):
    """
    Handles signup, login, logout, password reset.
    """
    permission_classes = [permissions.AllowAny]  # default for all actions

    # -------------------------
    # Signup (public)
    # -------------------------
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_data = UserSerializer(user).data
        return Response(
            {"message": "Account created successfully.", "user": user_data},
            status=status.HTTP_201_CREATED
        )

    # -------------------------
    # Login (public)
    # -------------------------
    @action(detail=False, methods=["post"], url_path="login")
    def login_user(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(
            {"message": "Login successful", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK
        )

    # -------------------------
    # Logout (requires authentication)
    # -------------------------
    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[permissions.IsAuthenticated])
    def logout_user(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    # Password Reset Request
    # -------------------------
    @action(detail=False, methods=["post"], url_path="password-reset")
    def password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            try:
                check_rate_limit(user, "password_reset", limit=3, period_seconds=3600, request=request)
            except RateLimitExceeded:
                return Response(
                    {"error": "Too many password reset attempts. Contact admin."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f"/api/users/auth/reset/{uid}/{token}/")

            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email="noreply@example.com",
                recipient_list=[email],
            )
        except User.DoesNotExist:
            # Always return generic message to avoid email enumeration
            pass

        return Response({"detail": "Password reset link sent"}, status=status.HTTP_200_OK)

    # -------------------------
    # Set New Password
    # -------------------------
    @action(
        detail=False,
        methods=["post"],
        url_path=r"reset/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)",
        url_name="set-new-password"
    )
    def set_new_password(self, request, uidb64=None, token=None):
        serializer = SetNewPasswordSerializer(
            data=request.data,
            context={'uidb64': uidb64, 'token': token}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )


# -------------------------
# Users ViewSet (Admin-only)
# -------------------------
class UsersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Admins can list, retrieve, update, and delete users.
    But cannot create new users via /users/.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------
# UserFile ViewSet
# -------------------------
class UserFileViewSet(viewsets.ModelViewSet):
    serializer_class = UserFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return UserFile.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return UserFile.objects.none()

        return UserFile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------
# Profile API
# -------------------------
class ProfileAPIView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def retrieve_profile(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["put"])
    def update_profile(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
