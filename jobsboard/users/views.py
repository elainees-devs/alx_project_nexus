#jobsboard/users/views.py
import logging
from django.http import JsonResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404

from .models import UserFile
from .serializers import (
    UserSerializer, ProfileSerializer, UserFileSerializer,
    SignUpSerializer, LoginSerializer,
    PasswordResetRequestSerializer, SetNewPasswordSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()

# -------------------------
# Home Views
# -------------------------
def home(request):
    return JsonResponse({
        "message": "Welcome to the JobsBoard API",
        "instructions": "Use /api/users/ to access user endpoints."
    })

def users_home(request):
    return JsonResponse({
        "message": "Welcome to the Users API",
        "endpoints": {
            "signup": "/api/users/signup/",
            "login": "/api/users/login/",
            "logout": "/api/users/logout/",
            "password-reset": "/api/users/password-reset/",
            "set-new-password": "/api/users/reset/<uidb64>/<token>/",
            "profile": "/api/users/profile/"
        }
    })


# -------------------------
# Users ViewSet (Admin-only)
# -------------------------
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------
# UserFile ViewSet
# -------------------------
class UserFileViewSet(ModelViewSet):
    serializer_class = UserFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return UserFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------
# Signup API
# -------------------------
class SignUpAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Register a new user")
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------
# Login API
# -------------------------
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Login user")
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({"username": user.username, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------
# Logout API
# -------------------------
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="Logout user")
    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


# -------------------------
# Password Reset APIs
# -------------------------
class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Request password reset email")
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(f"/api/users/reset/{uid}/{token}/")
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_link}",
                    from_email="noreply@example.com",
                    recipient_list=[email],
                )
            except User.DoesNotExist:
                pass
            return Response({"detail": "Password reset link sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Set new password")
    def post(self, request, uidb64, token):
        serializer = SetNewPasswordSerializer(data=request.data, context={'uidb64': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------
# Profile API
# -------------------------
class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="Get user profile")
    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Update user profile")
    def put(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
