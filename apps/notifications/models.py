from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """Notification model."""

    NOTIFICATION_TYPE_CHOICES = [
        ("info", "Information"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("security", "Security"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default="info"
    )
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)

    # Generic foreign key for related objects
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
            models.Index(fields=["notification_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NotificationTemplate(models.Model):
    """Notification template model."""

    name = models.CharField(max_length=100, unique=True)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES, default="info"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "notification_templates"

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """User notification preferences."""

    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("push", "Push Notification"),
        ("sms", "SMS"),
        ("in_app", "In-App"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    notification_type = models.CharField(
        max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preferences"
        unique_together = ["user", "channel", "notification_type"]

    def __str__(self):
        return f"{self.user.email} - {self.channel} - {self.notification_type}"
