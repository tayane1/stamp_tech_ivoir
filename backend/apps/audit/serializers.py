from rest_framework import serializers
from .models import AuditLog, SecurityEvent, SystemMetrics


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""

    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "action",
            "resource_type",
            "resource_id",
            "description",
            "ip_address",
            "user_agent",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SecurityEventSerializer(serializers.ModelSerializer):
    """Serializer for SecurityEvent model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    resolved_by_email = serializers.CharField(
        source="resolved_by.email", read_only=True
    )

    class Meta:
        model = SecurityEvent
        fields = [
            "id",
            "user",
            "user_email",
            "event_type",
            "severity",
            "description",
            "ip_address",
            "user_agent",
            "metadata",
            "resolved",
            "resolved_at",
            "resolved_by",
            "resolved_by_email",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer for SystemMetrics model."""

    class Meta:
        model = SystemMetrics
        fields = [
            "id",
            "metric_name",
            "metric_value",
            "metric_unit",
            "metadata",
            "recorded_at",
        ]
        read_only_fields = ["id", "recorded_at"]
