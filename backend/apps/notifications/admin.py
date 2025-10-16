from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationTemplate, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "title",
        "notification_type_status",
        "is_read_status",
        "is_important",
        "created_at",
    ]
    list_filter = [
        "notification_type",
        "is_read",
        "is_important",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "title",
        "message",
    ]
    readonly_fields = [
        "created_at",
        "read_at",
    ]
    raw_id_fields = ["user"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread", "mark_as_important"]

    def notification_type_status(self, obj):
        """Affiche le type de notification avec une couleur"""
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red",
            "security": "darkred",
        }
        color = colors.get(obj.notification_type, "black")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_notification_type_display(),
        )

    notification_type_status.short_description = "Type"

    def is_read_status(self, obj):
        """Affiche le statut de lecture avec une couleur"""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Lu</span>')
        else:
            return format_html('<span style="color: red;">✗ Non lu</span>')

    is_read_status.short_description = "Statut"

    def mark_as_read(self, request, queryset):
        """Marque les notifications comme lues"""
        from django.utils import timezone

        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} notifications marquées comme lues.")

    mark_as_read.short_description = "Marquer comme lues"

    def mark_as_unread(self, request, queryset):
        """Marque les notifications comme non lues"""
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{updated} notifications marquées comme non lues.")

    mark_as_unread.short_description = "Marquer comme non lues"

    def mark_as_important(self, request, queryset):
        """Marque les notifications comme importantes"""
        updated = queryset.update(is_important=True)
        self.message_user(
            request, f"{updated} notifications marquées comme importantes."
        )

    mark_as_important.short_description = "Marquer comme importantes"


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "title_template",
        "notification_type_status",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "notification_type",
        "is_active",
        "created_at",
    ]
    search_fields = ["name", "title_template", "message_template"]
    readonly_fields = ["created_at"]
    actions = ["activate_templates", "deactivate_templates"]

    def notification_type_status(self, obj):
        """Affiche le type de notification avec une couleur"""
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red",
            "security": "darkred",
        }
        color = colors.get(obj.notification_type, "black")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_notification_type_display(),
        )

    notification_type_status.short_description = "Type"

    def activate_templates(self, request, queryset):
        """Active les templates sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} templates activés avec succès.")

    activate_templates.short_description = "Activer les templates sélectionnés"

    def deactivate_templates(self, request, queryset):
        """Désactive les templates sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} templates désactivés avec succès.")

    deactivate_templates.short_description = "Désactiver les templates sélectionnés"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "channel",
        "notification_type_status",
        "is_enabled",
    ]
    list_filter = [
        "channel",
        "notification_type",
        "is_enabled",
    ]
    search_fields = ["user__email"]
    raw_id_fields = ["user"]
    actions = ["enable_preferences", "disable_preferences"]

    def notification_type_status(self, obj):
        """Affiche le type de notification avec une couleur"""
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red",
            "security": "darkred",
        }
        color = colors.get(obj.notification_type, "black")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_notification_type_display(),
        )

    notification_type_status.short_description = "Type"

    def enable_preferences(self, request, queryset):
        """Active les préférences sélectionnées"""
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f"{updated} préférences activées avec succès.")

    enable_preferences.short_description = "Activer les préférences sélectionnées"

    def disable_preferences(self, request, queryset):
        """Désactive les préférences sélectionnées"""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f"{updated} préférences désactivées avec succès.")

    disable_preferences.short_description = "Désactiver les préférences sélectionnées"
