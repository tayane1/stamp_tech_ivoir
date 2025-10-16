from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, SecurityEvent, SystemMetrics


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "action",
        "resource_type",
        "resource_id",
        "ip_address",
        "created_at",
    ]
    list_filter = [
        "action",
        "resource_type",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "resource_type",
        "resource_id",
        "description",
        "ip_address",
    ]
    readonly_fields = [
        "user",
        "action",
        "resource_type",
        "resource_id",
        "description",
        "ip_address",
        "user_agent",
        "metadata",
        "created_at",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        """Empêche l'ajout manuel de logs d'audit"""
        return False

    def has_change_permission(self, request, obj=None):
        """Empêche la modification des logs d'audit"""
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = [
        "event_type",
        "severity_status",
        "user",
        "ip_address",
        "resolved_status",
        "created_at",
    ]
    list_filter = [
        "event_type",
        "severity",
        "resolved",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "description",
        "ip_address",
    ]
    readonly_fields = [
        "user",
        "event_type",
        "severity",
        "description",
        "ip_address",
        "user_agent",
        "metadata",
        "created_at",
    ]
    raw_id_fields = ["user", "resolved_by"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    actions = ["mark_as_resolved", "mark_as_unresolved"]

    def severity_status(self, obj):
        """Affiche la sévérité avec une couleur"""
        colors = {
            "low": "green",
            "medium": "orange",
            "high": "red",
            "critical": "darkred",
        }
        color = colors.get(obj.severity, "black")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_severity_display()
        )

    severity_status.short_description = "Sévérité"

    def resolved_status(self, obj):
        """Affiche le statut de résolution avec une couleur"""
        if obj.resolved:
            return format_html('<span style="color: green;">✓ Résolu</span>')
        else:
            return format_html('<span style="color: red;">✗ Non résolu</span>')

    resolved_status.short_description = "Statut"

    def mark_as_resolved(self, request, queryset):
        """Marque les événements comme résolus"""
        from django.utils import timezone

        updated = queryset.update(
            resolved=True, resolved_at=timezone.now(), resolved_by=request.user
        )
        self.message_user(request, f"{updated} événements marqués comme résolus.")

    mark_as_resolved.short_description = "Marquer comme résolus"

    def mark_as_unresolved(self, request, queryset):
        """Marque les événements comme non résolus"""
        updated = queryset.update(resolved=False, resolved_at=None, resolved_by=None)
        self.message_user(request, f"{updated} événements marqués comme non résolus.")

    mark_as_unresolved.short_description = "Marquer comme non résolus"


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "metric_name",
        "metric_value",
        "metric_unit",
        "recorded_at",
    ]
    list_filter = [
        "metric_name",
        "recorded_at",
    ]
    search_fields = ["metric_name", "metric_unit"]
    readonly_fields = ["recorded_at"]
    ordering = ["-recorded_at"]
    date_hierarchy = "recorded_at"
