from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
import pyotp
import qrcode
import io
import base64

from .models import User, TwoFactorBackupCode, LoginAttempt
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    TwoFactorSetupSerializer,
    TwoFactorVerificationSerializer,
    BackupCodeSerializer,
    LoginAttemptSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create auth token
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    """User login endpoint with 2FA support."""

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data["user"]
    two_factor_code = serializer.validated_data.get("two_factor_code", "")

    # Track login attempt
    login_attempt = LoginAttempt.objects.create(
        user=user,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        success=False,
    )

    # Check if 2FA is enabled
    if user.is_2fa_enabled:
        if not two_factor_code:
            login_attempt.save()
            return Response(
                {"message": "Two-factor authentication required", "requires_2fa": True},
                status=status.HTTP_200_OK,
            )

        # Verify 2FA code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(two_factor_code):
            # Check backup codes
            backup_code = TwoFactorBackupCode.objects.filter(
                user=user, code=two_factor_code, is_used=False
            ).first()

            if not backup_code:
                login_attempt.save()
                return Response(
                    {"error": "Invalid two-factor authentication code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mark backup code as used
            backup_code.is_used = True
            backup_code.save()

    # Login successful
    login_attempt.success = True
    login_attempt.save()

    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {"user": UserSerializer(user).data, "token": token.key},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def setup_2fa(request):
    """Setup two-factor authentication."""

    user = request.user

    if user.is_2fa_enabled:
        return Response(
            {"error": "Two-factor authentication is already enabled"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Generate secret
    secret = pyotp.random_base32()

    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="Stamp App"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()

    return Response(
        {"secret": secret, "qr_code": f"data:image/png;base64,{qr_code_data}"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def verify_2fa_setup(request):
    """Verify and enable 2FA setup."""

    serializer = TwoFactorVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    secret = request.data.get("secret")
    code = serializer.validated_data["code"]

    if not secret:
        return Response(
            {"error": "Secret is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the code
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        return Response(
            {"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Enable 2FA
    user.two_factor_secret = secret
    user.is_2fa_enabled = True
    user.save()

    # Generate backup codes
    backup_codes = []
    for _ in range(10):
        code = pyotp.random_base32()[:8].upper()
        TwoFactorBackupCode.objects.create(user=user, code=code)
        backup_codes.append(code)

    return Response(
        {
            "message": "Two-factor authentication enabled successfully",
            "backup_codes": backup_codes,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def disable_2fa(request):
    """Disable two-factor authentication."""

    user = request.user

    if not user.is_2fa_enabled:
        return Response(
            {"error": "Two-factor authentication is not enabled"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Disable 2FA
    user.is_2fa_enabled = False
    user.two_factor_secret = None
    user.save()

    # Delete backup codes
    TwoFactorBackupCode.objects.filter(user=user).delete()

    return Response(
        {"message": "Two-factor authentication disabled successfully"},
        status=status.HTTP_200_OK,
    )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """User logout endpoint."""

    try:
        request.user.auth_token.delete()
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    except:
        return Response(
            {"error": "Error during logout"}, status=status.HTTP_400_BAD_REQUEST
        )
