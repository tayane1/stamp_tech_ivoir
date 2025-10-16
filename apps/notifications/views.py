from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone

from .models import Notification, NotificationTemplate, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationTemplateSerializer,
    NotificationPreferenceSerializer,
)


class NotificationListView(generics.ListAPIView):
    """List user notifications."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update notification."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.data.get("is_read") and not instance.is_read:
            instance.mark_as_read()
        return Response(NotificationSerializer(instance).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_all_as_read(request):
    """Mark all notifications as read for the user."""

    updated_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return Response(
        {"message": f"Marked {updated_count} notifications as read"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def notification_count(request):
    """Get unread notification count."""

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)


class NotificationTemplateListView(generics.ListAPIView):
    """List notification templates."""

    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only admin users can view templates
        if not self.request.user.is_staff:
            return NotificationTemplate.objects.none()

        return NotificationTemplate.objects.filter(is_active=True)


class NotificationPreferenceListView(generics.ListCreateAPIView):
    """List and create notification preferences."""

    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete notification preference."""

    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def send_notification(request):
    """Send notification to user."""

    # Only admin users can send notifications
    if not request.user.is_staff:
        return Response(
            {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
        )

    serializer = NotificationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notification = serializer.save()

    return Response(
        NotificationSerializer(notification).data, status=status.HTTP_201_CREATED
    )
