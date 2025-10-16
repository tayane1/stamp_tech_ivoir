from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class AuditLog(models.Model):
    """Audit log model for tracking system activities."""

    ACTION_CHOICES = [
        ("USER_LOGIN", "Connexion"),
        ("QR_GENERATED", "QR généré"),
        ("QR_VERIFIED", "QR vérifié"),
        ("QR_REVOKED", "QR révoqué"),
        ("create", "Create"),
        ("read", "Read"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("verify", "Verify"),
        ("revoke", "Revoke"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)  # Model name
    resource_id = models.CharField(max_length=100)  # Object ID
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        return f"{self.user.email if self.user else 'Anonymous'} - {self.action} - {self.resource_type}"


class SecurityEvent(models.Model):
    """Security events model for tracking security-related activities."""

    EVENT_TYPE_CHOICES = [
        ("failed_login", "Failed Login"),
        ("suspicious_activity", "Suspicious Activity"),
        ("data_breach", "Data Breach"),
        ("unauthorized_access", "Unauthorized Access"),
        ("password_change", "Password Change"),
        ("2fa_enabled", "2FA Enabled"),
        ("2fa_disabled", "2FA Disabled"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, default="medium"
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField(default=dict)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_events",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "security_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "severity"]),
            models.Index(fields=["resolved", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.created_at}"


class SystemMetrics(models.Model):
    """System metrics model for tracking system performance."""

    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "system_metrics"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["metric_name", "recorded_at"]),
        ]

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"
