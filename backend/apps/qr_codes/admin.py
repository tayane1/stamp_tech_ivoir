from django.contrib import admin
from django.utils.html import format_html
from .models import QRCode, QRVerification, QRCodeTemplate


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        "unique_code",
        "user",
        "company",
        "status",
        "created_at",
        "expires_at",
    ]
    list_filter = ["status", "created_at", "expires_at"]
    search_fields = ["unique_code", "user__email", "company__name"]
    readonly_fields = [
        "id",
        "unique_code",
        "encrypted_data",
        "signature",
        "hash_value",
        "salt",
        "created_at",
    ]
    raw_id_fields = ["user", "company"]
    actions = ["revoke_qr_codes", "suspend_qr_codes"]

    def revoke_qr_codes(self, request, queryset):
        """Révoque les QR codes sélectionnés"""
        from django.utils import timezone

        updated = queryset.update(
            status=QRCode.Status.REVOKED, revoked_at=timezone.now()
        )
        self.message_user(request, f"{updated} QR codes révoqués avec succès.")

    revoke_qr_codes.short_description = "Révoquer les QR codes sélectionnés"

    def suspend_qr_codes(self, request, queryset):
        """Suspend les QR codes sélectionnés"""
        updated = queryset.update(status=QRCode.Status.SUSPENDED)
        self.message_user(request, f"{updated} QR codes suspendus avec succès.")

    suspend_qr_codes.short_description = "Suspendre les QR codes sélectionnés"


@admin.register(QRVerification)
class QRVerificationAdmin(admin.ModelAdmin):
    list_display = ["qr_code", "is_valid", "ip_address", "verified_at"]
    list_filter = ["is_valid", "verified_at"]
    search_fields = ["qr_code__unique_code", "ip_address"]
    readonly_fields = ["verified_at"]
    raw_id_fields = ["qr_code"]


@admin.register(QRCodeTemplate)
class QRCodeTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]
