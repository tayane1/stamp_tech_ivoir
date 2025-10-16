from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, TwoFactorBackupCode, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "two_factor_status",
        "is_active",
        "is_staff",
        "date_joined",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "two_factor_enabled",
        "date_joined",
    ]
    search_fields = ["email", "username", "first_name", "last_name"]
    readonly_fields = ["id", "date_joined", "last_login"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "email", "phone")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Sécurité", {"fields": ("two_factor_enabled", "two_factor_secret")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    def two_factor_status(self, obj):
        """Affiche le statut 2FA avec une couleur"""
        if obj.two_factor_enabled:
            return format_html('<span style="color: green;">✓ Activé</span>')
        else:
            return format_html('<span style="color: red;">✗ Désactivé</span>')

    two_factor_status.short_description = "2FA"


@admin.register(TwoFactorBackupCode)
class TwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "code",
        "is_used",
        "created_at",
    ]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email", "code"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "ip_address",
        "success_status",
        "created_at",
    ]
    list_filter = ["success", "created_at"]
    search_fields = ["user__email", "ip_address"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user"]
    ordering = ["-created_at"]

    def success_status(self, obj):
        """Affiche le statut de connexion avec une couleur"""
        if obj.success:
            return format_html('<span style="color: green;">✓ Succès</span>')
        else:
            return format_html('<span style="color: red;">✗ Échec</span>')

    success_status.short_description = "Statut"
