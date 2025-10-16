from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """Utilisateur avec 2FA"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = _("Utilisateur")

    def __str__(self):
        return self.email


class TwoFactorBackupCode(models.Model):
    """Backup codes for 2FA."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="backup_codes"
    )
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "two_factor_backup_codes"

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class LoginAttempt(models.Model):
    """Track login attempts for security."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_attempts"
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "login_attempts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.ip_address} - {'Success' if self.success else 'Failed'}"
