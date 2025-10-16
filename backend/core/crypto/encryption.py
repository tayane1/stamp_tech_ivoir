"""
Core cryptographic utilities
"""

import hashlib
import hmac
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import os


class EncryptionService:
    """Service for encryption and decryption operations."""

    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self):
        """Get or create encryption key."""

        # In production, this should be stored securely
        key = getattr(settings, "ENCRYPTION_KEY", None)
        if not key:
            key = Fernet.generate_key()
            # In production, store this key securely
        return key

    def encrypt(self, data):
        """Encrypt data."""

        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, dict):
            import json

            data = json.dumps(data).encode()

        return self.cipher.encrypt(data).decode()

    def decrypt(self, encrypted_data):
        """Decrypt data."""

        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())

            # Try to decode as JSON first
            try:
                import json

                return json.loads(decrypted_bytes.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return decrypted_bytes.decode()

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def hash_data(self, data):
        """Generate SHA-256 hash of data."""

        if isinstance(data, str):
            data = data.encode()

        return hashlib.sha256(data).hexdigest()

    def generate_hmac(self, data, secret_key=None):
        """Generate HMAC for data integrity."""

        if secret_key is None:
            secret_key = getattr(settings, "HMAC_SECRET_KEY", "default-secret-key")

        if isinstance(data, str):
            data = data.encode()

        return hmac.new(secret_key.encode(), data, hashlib.sha256).hexdigest()

    def verify_hmac(self, data, hmac_value, secret_key=None):
        """Verify HMAC."""

        expected_hmac = self.generate_hmac(data, secret_key)
        return hmac.compare_digest(expected_hmac, hmac_value)

    def generate_secure_token(self, length=32):
        """Generate a secure random token."""

        return secrets.token_urlsafe(length)

    def generate_nonce(self):
        """Generate a nonce for cryptographic operations."""

        return secrets.token_hex(16)


class PasswordService:
    """Service for password operations."""

    @staticmethod
    def hash_password(password, salt=None):
        """Hash password with salt."""

        if salt is None:
            salt = secrets.token_hex(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt

    @staticmethod
    def verify_password(password, hashed_password, salt):
        """Verify password against hash."""

        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )

            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode() == hashed_password
        except Exception:
            return False


class DigitalSignatureService:
    """Service for digital signatures."""

    def __init__(self):
        self.private_key = self._get_private_key()
        self.public_key = self._get_public_key()

    def _get_private_key(self):
        """Get private key for signing."""
        # Implementation depends on your key management system
        return None

    def _get_public_key(self):
        """Get public key for verification."""
        # Implementation depends on your key management system
        return None

    def sign_data(self, data):
        """Sign data with private key."""
        # Implementation for digital signature
        pass

    def verify_signature(self, data, signature):
        """Verify digital signature."""
        # Implementation for signature verification
        pass
