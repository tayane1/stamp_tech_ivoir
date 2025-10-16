from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class QRCode(models.Model):
    """QR Code sécurisé"""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Actif")
        SUSPENDED = "SUSPENDED", _("Suspendu")
        REVOKED = "REVOKED", _("Révoqué")
        EXPIRED = "EXPIRED", _("Expiré")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    unique_code = models.CharField(max_length=50, unique=True, db_index=True)

    # Données chiffrées
    encrypted_data = models.TextField()
    signature = models.TextField()
    hash_value = models.CharField(max_length=64)
    salt = models.CharField(max_length=64)

    # Métadonnées
    version = models.CharField(max_length=10, default="1.0")
    algorithm = models.CharField(max_length=50, default="AES256-GCM")

    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="qr_codes")
    company = models.ForeignKey(
        "companies.Company", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Statut
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    # Image QR code
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    class Meta:
        db_table = "qr_codes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["unique_code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return self.unique_code

    def is_valid(self):
        """Vérifie si le QR est valide"""
        return self.status == self.Status.ACTIVE and self.expires_at > timezone.now()


class QRVerification(models.Model):
    """Historique des vérifications"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    qr_code = models.ForeignKey(
        QRCode, on_delete=models.CASCADE, related_name="verifications"
    )

    is_valid = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)

    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "qr_verifications"
        ordering = ["-verified_at"]
        indexes = [
            models.Index(fields=["qr_code", "verified_at"]),
        ]

    def __str__(self):
        return f"{self.qr_code.unique_code} - {self.ip_address} - {'Valid' if self.is_valid else 'Invalid'}"


class QRCodeTemplate(models.Model):
    """Templates for QR code generation."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "qr_code_templates"

    def __str__(self):
        return self.name
