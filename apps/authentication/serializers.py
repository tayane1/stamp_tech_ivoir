from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, TwoFactorBackupCode, LoginAttempt


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_2fa_enabled",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField()
    two_factor_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include email and password.")


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup."""

    secret = serializers.CharField()
    verification_code = serializers.CharField(max_length=6)


class TwoFactorVerificationSerializer(serializers.Serializer):
    """Serializer for 2FA verification."""

    code = serializers.CharField(max_length=6)


class BackupCodeSerializer(serializers.ModelSerializer):
    """Serializer for backup codes."""

    class Meta:
        model = TwoFactorBackupCode
        fields = ["code", "is_used", "created_at"]
        read_only_fields = ["code", "created_at"]


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer for login attempts."""

    class Meta:
        model = LoginAttempt
        fields = ["ip_address", "user_agent", "success", "created_at"]
        read_only_fields = ["ip_address", "user_agent", "success", "created_at"]
