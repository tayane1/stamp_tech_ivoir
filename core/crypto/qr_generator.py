import secrets
import hashlib
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from django.conf import settings
import qrcode
from io import BytesIO


class SecureQRGenerator:
    """Générateur de QR codes sécurisés"""

    def __init__(self):
        self.encryption_key = self._load_encryption_key()
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()

    def generate(self, user, company=None, expires_days=365) -> Dict[str, Any]:
        """
        Génère un QR code sécurisé

        Args:
            user: User instance
            company: Company instance (optional)
            expires_days: Nombre de jours avant expiration

        Returns:
            Dict avec QR code et métadonnées
        """
        # 1. Génération ID unique
        unique_code = self._generate_unique_id()

        # 2. Création du payload
        payload = {
            "id": unique_code,
            "user_id": str(user.id),
            "company_id": str(company.id) if company else None,
            "timestamp": int(datetime.now().timestamp()),
            "expires_at": int(
                (datetime.now() + timedelta(days=expires_days)).timestamp()
            ),
            "version": "1.0",
        }

        # 3. Génération sel unique
        salt = secrets.token_bytes(32)

        # 4. Hachage avec sel
        hash_value = self._hash_payload(payload, salt)

        # 5. Chiffrement AES-256-GCM
        encrypted_data = self._encrypt(payload, hash_value)

        # 6. Signature RSA
        signature = self._sign(encrypted_data)

        # 7. Construction données finales
        qr_data = {
            "v": "1.0",
            "id": unique_code,
            "enc": "AES256-GCM",
            "data": encrypted_data,
            "sig": signature,
            "exp": (datetime.now() + timedelta(days=expires_days)).isoformat(),
            "iss": "STAMP-TECH-IVOIRE",
        }

        # 8. Génération image QR
        qr_image = self._generate_qr_image(qr_data)

        return {
            "unique_code": unique_code,
            "encrypted_data": encrypted_data,
            "signature": signature,
            "hash_value": hash_value.hex(),
            "salt": salt.hex(),
            "qr_image": qr_image,
            "qr_data": qr_data,
            "expires_at": datetime.now() + timedelta(days=expires_days),
        }

    def _generate_unique_id(self) -> str:
        """Génère un ID unique au format ST-CI-YYYY-XXXXXX"""
        year = datetime.now().year
        random_part = secrets.token_hex(4).upper()
        return f"ST-CI-{year}-{random_part}"

    def _hash_payload(self, payload: Dict, salt: bytes) -> bytes:
        """Hash le payload avec SHA-256 et sel"""
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.pbkdf2_hmac("sha256", data, salt, 100000)

    def _encrypt(self, payload: Dict, key: bytes) -> str:
        """Chiffre le payload avec AES-256-GCM"""
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)

        plaintext = json.dumps(payload).encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Combine nonce + ciphertext
        encrypted = nonce + ciphertext
        return base64.b64encode(encrypted).decode("utf-8")

    def _sign(self, data: str) -> str:
        """Signe les données avec RSA"""
        signature = self.private_key.sign(
            data.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _generate_qr_image(self, qr_data: Dict) -> bytes:
        """Génère l'image QR code"""
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        # Encode data en base64
        data_str = base64.b64encode(json.dumps(qr_data).encode("utf-8")).decode("utf-8")

        qr.add_data(data_str)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#059669", back_color="white")  # Vert émeraude

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def _load_encryption_key(self) -> bytes:
        """Charge la clé de chiffrement"""
        return bytes.fromhex(settings.ENCRYPTION_KEY)

    def _load_private_key(self):
        """Charge la clé privée RSA"""
        with open(settings.RSA_PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def _load_public_key(self):
        """Charge la clé publique RSA"""
        with open(settings.RSA_PUBLIC_KEY_PATH, "rb") as f:
            return serialization.load_pem_public_key(f.read())


class QRVerifier:
    """Vérificateur de QR codes"""

    def __init__(self):
        self.public_key = self._load_public_key()

    def verify(self, qr_data_str: str, qr_code_instance=None) -> Dict[str, Any]:
        """
        Vérifie un QR code

        Returns:
            Dict avec résultat de vérification
        """
        try:
            # 1. Decode base64
            decoded = base64.b64decode(qr_data_str)
            qr_data = json.loads(decoded)

            # 2. Vérifier signature
            if not self._verify_signature(qr_data["data"], qr_data["sig"]):
                return {"valid": False, "error": "Invalid signature"}

            # 3. Vérifier en base de données
            from apps.qr_codes.models import QRCode

            try:
                qr_code = QRCode.objects.select_related("user", "company").get(
                    unique_code=qr_data["id"]
                )
            except QRCode.DoesNotExist:
                return {"valid": False, "error": "QR code not found"}

            # 4. Vérifier statut
            if not qr_code.is_valid():
                return {
                    "valid": False,
                    "error": f"QR code is {qr_code.status.lower()}",
                }

            # 5. Déchiffrer et retourner infos
            return {
                "valid": True,
                "data": {
                    "holder": f"{qr_code.user.first_name} {qr_code.user.last_name}",
                    "email": qr_code.user.email,
                    "company": qr_code.company.name if qr_code.company else None,
                    "issued_at": qr_code.created_at.isoformat(),
                    "expires_at": qr_code.expires_at.isoformat(),
                },
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _verify_signature(self, data: str, signature: str) -> bool:
        """Vérifie la signature RSA"""
        try:
            sig_bytes = base64.b64decode(signature)
            self.public_key.verify(
                sig_bytes,
                data.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except:
            return False

    def _load_public_key(self):
        """Charge la clé publique"""
        from django.conf import settings

        with open(settings.RSA_PUBLIC_KEY_PATH, "rb") as f:
            return serialization.load_pem_public_key(f.read())
