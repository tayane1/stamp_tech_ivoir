"""
QR Code Generator Service
"""

import qrcode
import hashlib
import uuid
from django.utils import timezone
from django.core.files.base import ContentFile
import io
import base64

from ..models import QRCode
from core.crypto.encryption import EncryptionService


class QRCodeGenerator:
    """Service for generating QR codes."""

    def __init__(self):
        self.encryption_service = EncryptionService()

    def generate_qr_code(self, user, title, description, data, expires_at=None):
        """Generate a new QR code."""

        # Encrypt the data
        encrypted_data = self.encryption_service.encrypt(data)

        # Generate hash for verification
        hash_value = self._generate_hash(encrypted_data, user.id)

        # Create QR code instance
        qr_code = QRCode.objects.create(
            user=user,
            title=title,
            description=description,
            data=encrypted_data,
            hash_value=hash_value,
            expires_at=expires_at,
        )

        return qr_code

    def generate_qr_image(self, qr_code):
        """Generate QR code image."""

        # Create QR code data string
        qr_data = f"{qr_code.id}:{qr_code.hash_value}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def _generate_hash(self, data, user_id):
        """Generate SHA-256 hash for data verification."""

        hash_input = f"{data}:{user_id}:{timezone.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def generate_from_template(self, user, template, template_data):
        """Generate QR code from template."""

        # Process template data
        processed_data = self._process_template(template.template_data, template_data)

        return self.generate_qr_code(
            user=user,
            title=processed_data.get("title", "Generated QR Code"),
            description=processed_data.get("description", ""),
            data=processed_data.get("data", {}),
            expires_at=processed_data.get("expires_at"),
        )

    def _process_template(self, template_data, user_data):
        """Process template with user data."""

        processed = template_data.copy()

        # Replace placeholders with user data
        for key, value in user_data.items():
            if isinstance(value, str):
                processed["title"] = processed.get("title", "").replace(
                    f"{{{key}}}", value
                )
                processed["description"] = processed.get("description", "").replace(
                    f"{{{key}}}", value
                )

        return processed
