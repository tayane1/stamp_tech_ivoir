"""
QR Code Verifier Service
"""

from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import QRCode, QRCodeVerification
from core.crypto.encryption import EncryptionService


class QRCodeVerifier:
    """Service for verifying QR codes."""

    def __init__(self):
        self.encryption_service = EncryptionService()

    def verify_qr_code(self, qr_code, verification_data, request):
        """Verify a QR code."""

        verification_result = {"is_valid": False, "message": "", "data": None}

        try:
            # Check if QR code exists and is active
            if not qr_code.is_valid:
                verification_result["message"] = "QR code is not valid or has expired"
                return verification_result

            # Verify hash integrity
            if not self._verify_hash_integrity(qr_code):
                verification_result["message"] = "QR code data integrity check failed"
                return verification_result

            # Decrypt and return data
            decrypted_data = self.encryption_service.decrypt(qr_code.data)

            # Additional verification logic can be added here
            if self._perform_additional_verification(qr_code, verification_data):
                verification_result["is_valid"] = True
                verification_result["message"] = "QR code verified successfully"
                verification_result["data"] = decrypted_data
            else:
                verification_result["message"] = "Additional verification failed"

        except Exception as e:
            verification_result["message"] = f"Verification error: {str(e)}"

        return verification_result

    def _verify_hash_integrity(self, qr_code):
        """Verify the hash integrity of the QR code."""

        try:
            # Recalculate hash
            hash_input = (
                f"{qr_code.data}:{qr_code.user.id}:{qr_code.created_at.isoformat()}"
            )
            calculated_hash = self.encryption_service.hash_data(hash_input)

            return calculated_hash == qr_code.hash_value
        except Exception:
            return False

    def _perform_additional_verification(self, qr_code, verification_data):
        """Perform additional verification checks."""

        # Check if QR code has been used
        if qr_code.status == "used":
            return False

        # Check expiration
        if qr_code.is_expired:
            return False

        # Check if QR code is revoked
        if qr_code.status == "revoked":
            return False

        # Additional verification logic can be added here
        # For example: location verification, time-based verification, etc.

        return True

    def verify_qr_code_by_id_and_hash(self, qr_code_id, hash_value):
        """Verify QR code by ID and hash."""

        try:
            qr_code = QRCode.objects.get(id=qr_code_id, hash_value=hash_value)
            return self.verify_qr_code(qr_code, {}, None)
        except QRCode.DoesNotExist:
            return {"is_valid": False, "message": "QR code not found", "data": None}

    def get_verification_history(self, qr_code):
        """Get verification history for a QR code."""

        return QRCodeVerification.objects.filter(qr_code=qr_code).order_by(
            "-created_at"
        )

    def is_qr_code_compromised(self, qr_code):
        """Check if QR code might be compromised."""

        # Check for multiple failed verification attempts
        recent_failed_attempts = QRCodeVerification.objects.filter(
            qr_code=qr_code,
            verification_result=False,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1),
        ).count()

        return recent_failed_attempts > 5
