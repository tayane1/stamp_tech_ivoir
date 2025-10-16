from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification-list"),
    path(
        "<int:pk>/", views.NotificationDetailView.as_view(), name="notification-detail"
    ),
    path("mark-all-read/", views.mark_all_as_read, name="mark-all-read"),
    path("count/", views.notification_count, name="notification-count"),
    path("send/", views.send_notification, name="send-notification"),
    path(
        "templates/", views.NotificationTemplateListView.as_view(), name="template-list"
    ),
    path(
        "preferences/",
        views.NotificationPreferenceListView.as_view(),
        name="preference-list",
    ),
    path(
        "preferences/<int:pk>/",
        views.NotificationPreferenceDetailView.as_view(),
        name="preference-detail",
    ),
]
