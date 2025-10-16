from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyMember


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sector",
        "member_count",
        "created_at",
        "updated_at",
    ]
    list_filter = ["sector", "created_at"]
    search_fields = ["name", "sector", "address"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def member_count(self, obj):
        """Affiche le nombre de membres de l'entreprise"""
        return obj.members.filter(is_active=True).count()

    member_count.short_description = "Nombre de membres"


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "company",
        "role",
        "is_active",
        "joined_at",
    ]
    list_filter = ["role", "is_active", "joined_at"]
    search_fields = ["user__email", "company__name"]
    readonly_fields = ["joined_at"]
    raw_id_fields = ["user", "company"]
    actions = ["activate_members", "deactivate_members"]

    def activate_members(self, request, queryset):
        """Active les membres sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} membres activés avec succès.")

    activate_members.short_description = "Activer les membres sélectionnés"

    def deactivate_members(self, request, queryset):
        """Désactive les membres sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} membres désactivés avec succès.")

    deactivate_members.short_description = "Désactiver les membres sélectionnés"
