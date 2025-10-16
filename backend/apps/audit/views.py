from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog, SecurityEvent, SystemMetrics
from .serializers import (
    AuditLogSerializer,
    SecurityEventSerializer,
    SystemMetricsSerializer,
)


class AuditLogListView(generics.ListAPIView):
    """List audit logs."""

    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show logs for the current user unless they're admin
        queryset = AuditLog.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        # Filter by date range if provided
        days = self.request.query_params.get("days", 30)
        try:
            days = int(days)
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)
        except ValueError:
            pass

        return queryset


class SecurityEventListView(generics.ListAPIView):
    """List security events."""

    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show events for the current user unless they're admin
        queryset = SecurityEvent.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset


class SecurityEventDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update security events."""

    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SecurityEvent.objects.all()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def resolve_security_event(request, pk):
    """Resolve a security event."""

    try:
        event = SecurityEvent.objects.get(pk=pk)
    except SecurityEvent.DoesNotExist:
        return Response(
            {"error": "Security event not found"}, status=status.HTTP_404_NOT_FOUND
        )

    event.resolved = True
    event.resolved_at = timezone.now()
    event.resolved_by = request.user
    event.save()

    return Response(
        {"message": "Security event resolved successfully"}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def audit_dashboard(request):
    """Get audit dashboard data."""

    # Get recent audit logs
    recent_logs = AuditLog.objects.filter(user=request.user).order_by("-created_at")[
        :10
    ]

    # Get security events
    security_events = SecurityEvent.objects.filter(
        user=request.user, resolved=False
    ).order_by("-created_at")[:5]

    # Get activity summary
    activity_summary = {
        "total_logs": AuditLog.objects.filter(user=request.user).count(),
        "recent_logs": recent_logs.count(),
        "unresolved_events": SecurityEvent.objects.filter(
            user=request.user, resolved=False
        ).count(),
    }

    return Response(
        {
            "activity_summary": activity_summary,
            "recent_logs": AuditLogSerializer(recent_logs, many=True).data,
            "security_events": SecurityEventSerializer(security_events, many=True).data,
        },
        status=status.HTTP_200_OK,
    )


class SystemMetricsListView(generics.ListAPIView):
    """List system metrics."""

    serializer_class = SystemMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only admin users can view system metrics
        if not self.request.user.is_staff:
            return SystemMetrics.objects.none()

        # Filter by metric name if provided
        metric_name = self.request.query_params.get("metric_name")
        if metric_name:
            return SystemMetrics.objects.filter(metric_name=metric_name)

        return SystemMetrics.objects.all()
