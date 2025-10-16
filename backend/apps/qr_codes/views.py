from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Count, Q
from django.core.files.base import ContentFile

from .models import QRCode, QRVerification, QRCodeTemplate
from .serializers import QRCodeSerializer, QRVerificationSerializer
from core.crypto.qr_generator import SecureQRGenerator, QRVerifier
from apps.audit.models import AuditLog


class QRCodeViewSet(viewsets.ModelViewSet):
    """API pour gérer les QR codes"""

    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtre les QR codes par utilisateur"""
        return (
            QRCode.objects.filter(user=self.request.user)
            .select_related("company")
            .prefetch_related("verifications")
        )

    def create(self, request):
        """Génère un nouveau QR code"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Générer QR sécurisé
        generator = SecureQRGenerator()
        company = serializer.validated_data.get("company")

        qr_result = generator.generate(
            user=request.user, company=company, expires_days=365
        )

        # Sauvegarder en base
        qr_code = QRCode.objects.create(
            user=request.user,
            company=company,
            unique_code=qr_result["unique_code"],
            encrypted_data=qr_result["encrypted_data"],
            signature=qr_result["signature"],
            hash_value=qr_result["hash_value"],
            salt=qr_result["salt"],
            expires_at=qr_result["expires_at"],
        )

        # Sauvegarder image
        qr_code.qr_image.save(
            f"{qr_code.unique_code}.png", ContentFile(qr_result["qr_image"])
        )

        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.QR_GENERATED,
            entity_type="QRCode",
            entity_id=qr_code.id,
            ip_address=self.get_client_ip(request),
        )

        return Response(QRCodeSerializer(qr_code).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """Révoque un QR code"""
        qr_code = self.get_object()
        qr_code.status = QRCode.Status.REVOKED
        qr_code.revoked_at = timezone.now()
        qr_code.save()

        return Response({"status": "revoked"})

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Statistiques des QR codes"""
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "active": queryset.filter(status=QRCode.Status.ACTIVE).count(),
            "revoked": queryset.filter(status=QRCode.Status.REVOKED).count(),
            "expired": queryset.filter(status=QRCode.Status.EXPIRED).count(),
            "verifications_today": QRVerification.objects.filter(
                qr_code__user=request.user,
                verified_at__date=timezone.now().date(),
            ).count(),
        }

        return Response(stats)

    def get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class QRVerificationView(viewsets.GenericViewSet):
    """API publique de vérification"""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """Vérifie un QR code (endpoint public)"""
        qr_data = request.data.get("qr_data")

        if not qr_data:
            return Response(
                {"valid": False, "error": "Missing qr_data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier QR
        verifier = QRVerifier()
        result = verifier.verify(qr_data)

        # Logger la vérification
        if "data" in result:
            qr_code = QRCode.objects.get(unique_code=result["data"]["id"])

            QRVerification.objects.create(
                qr_code=qr_code,
                is_valid=result["valid"],
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            # Mettre à jour last_verified_at
            qr_code.last_verified_at = timezone.now()
            qr_code.save(update_fields=["last_verified_at"])

        return Response(result)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
