# jobsboard/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    class Meta:
        model = Profile
        fields = ['id', 'bio', 'location', 'birth_date', 'profile_image']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    profile = ProfileSerializer(read_only=True)  # include profile in user serializer

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'middle_name', 'last_name', 'role', 'profile']
        read_only_fields = ['id', 'role']


class SignUpSerializer(serializers.ModelSerializer):
    """Serializer for user sign-up."""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    profile = ProfileSerializer(read_only=True)  # include profile in signup response

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'middle_name', 'last_name', 'role', 'profile']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()  # Profile will be created automatically via signal
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Both username and password are required.")
        data['user'] = user
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class SetNewPasswordSerializer(serializers.Serializer):
    """Serializer for setting a new password."""
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
