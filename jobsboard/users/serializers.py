# jobsboard/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .models import Profile, UserFile
from rate_limit.services import check_rate_limit, RateLimitExceeded
from request_logs.models import RequestLog

User = get_user_model()

# ---------------------------------------------------------
# SignUpSerializer
# ---------------------------------------------------------
# Serializer for registering new users.
# - Ensures password and confirm_password match.
# - Handles creation of User instances with hashed passwords.
class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'middle_name', 'last_name', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# ---------------------------------------------------------
# LoginSerializer
# ---------------------------------------------------------
# Serializer for authenticating users.
# - Validates credentials against the database.
# - Implements rate-limiting for failed login attempts.
# - Logs failed login attempts for auditing.
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Attempt to get the user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Check failed login rate limit
        try:
            check_rate_limit(user, "failed_login", limit=5, period_seconds=15*60, request=self.context.get('request'))
        except RateLimitExceeded:
            raise serializers.ValidationError(
                "Account blocked: too many failed login attempts. Please contact admin."
            )

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            # Log failed attempt
            ip = self.context.get('request').META.get("REMOTE_ADDR", "unknown")
            RequestLog.objects.create(
                user=user,
                ip_address=ip,
                endpoint=self.context.get('request').path,
                method=self.context.get('request').method,
                status_code=401
            )
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = user
        return attrs


# ---------------------------------------------------------
# ProfileSerializer
# ---------------------------------------------------------
# Serializer for the Profile model.
# - Exposes bio, location, birth_date, and profile_image fields.
# - Read-only ID field.
class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    class Meta:
        model = Profile
        fields = ['id', 'bio', 'location', 'birth_date', 'profile_image']
        read_only_fields = ['id']


# ---------------------------------------------------------
# UserFileSerializer
# ---------------------------------------------------------
# Serializer for user-uploaded files (profile image, resume, CV).
# - Validates files against model-defined validators.
# - Ensures uploaded_at is read-only.
class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ['id', 'file_type', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def validate(self, attrs):
        file_type = attrs.get("file_type")
        file = attrs.get("file")

        # Use FILE_VALIDATORS from the model
        validators = UserFile.FILE_VALIDATORS.get(file_type)
        if validators:
            for validator in validators:
                validator(file)  # raise ValidationError if invalid

        return attrs

# ---------------------------------------------------------
# UserSerializer
# ---------------------------------------------------------
# Serializer for the User model.
# - Includes nested ProfileSerializer.
# - Exposes core user fields and role.
# - Read-only ID and role fields.
class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'middle_name', 'last_name', 'role', 'profile']
        read_only_fields = ['id', 'role']

# ---------------------------------------------------------
# PasswordResetRequestSerializer
# ---------------------------------------------------------
# Serializer for requesting a password reset.
# - Validates that the provided email exists in the system.
class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

# ---------------------------------------------------------
# SetNewPasswordSerializer
# ---------------------------------------------------------
# Serializer for setting a new password.
# - Validates that password and confirm_password match.
# - Validates the UID and token from the password reset link.
# - Updates the user's password if validation passes.

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid UID"})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        user.set_password(self.validated_data['password'])
        user.save()
        return user