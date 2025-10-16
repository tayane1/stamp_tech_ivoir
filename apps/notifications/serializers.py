from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "is_important",
            "metadata",
            "created_at",
            "read_at",
        ]
        read_only_fields = ["id", "created_at", "read_at"]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""

    class Meta:
        model = Notification
        fields = [
            "user",
            "title",
            "message",
            "notification_type",
            "is_important",
            "metadata",
        ]

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "name",
            "title_template",
            "message_template",
            "notification_type",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    class Meta:
        model = NotificationPreference
        fields = ["id", "channel", "notification_type", "is_enabled"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
