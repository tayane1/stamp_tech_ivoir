from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class Company(models.Model):
    """Entreprise"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    """Company membership model."""

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("member", "Member"),
        ("viewer", "Viewer"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="company_memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "company_members"
        unique_together = ["company", "user"]

    def __str__(self):
        return f"{self.user.email} - {self.company.name} ({self.role})"
