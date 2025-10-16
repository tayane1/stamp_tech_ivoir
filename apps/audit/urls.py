from django.urls import path
from . import views

app_name = "audit"

urlpatterns = [
    path("logs/", views.AuditLogListView.as_view(), name="audit-log-list"),
    path(
        "security-events/",
        views.SecurityEventListView.as_view(),
        name="security-event-list",
    ),
    path(
        "security-events/<int:pk>/",
        views.SecurityEventDetailView.as_view(),
        name="security-event-detail",
    ),
    path(
        "security-events/<int:pk>/resolve/",
        views.resolve_security_event,
        name="resolve-security-event",
    ),
    path("dashboard/", views.audit_dashboard, name="audit-dashboard"),
    path("metrics/", views.SystemMetricsListView.as_view(), name="system-metrics-list"),
]
