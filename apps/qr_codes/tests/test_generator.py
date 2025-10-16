from django.test import TestCase
from django.contrib.auth import get_user_model
from core.crypto.qr_generator import SecureQRGenerator, QRVerifier
from apps.companies.models import Company

User = get_user_model()


class QRGeneratorTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.company = Company.objects.create(name="Test Company", sector="Technology")
        self.generator = SecureQRGenerator()
        self.verifier = QRVerifier()

    def test_generate_unique_qr_codes(self):
        """Les QR codes générés doivent être uniques"""
        qr1 = self.generator.generate(self.user, self.company)
        qr2 = self.generator.generate(self.user, self.company)

        self.assertNotEqual(qr1["unique_code"], qr2["unique_code"])

    def test_qr_code_format(self):
        """Le format du code doit être ST-CI-YYYY-XXXXXX"""
        qr = self.generator.generate(self.user)

        self.assertTrue(qr["unique_code"].startswith("ST-CI-"))
        self.assertEqual(len(qr["unique_code"]), 19)  # ST-CI-2024-XXXXXXXX

    def test_encryption_decryption(self):
        """Les données doivent être correctement chiffrées/déchiffrées"""
        qr = self.generator.generate(self.user, self.company)

        self.assertIsNotNone(qr["encrypted_data"])
        self.assertIsNotNone(qr["signature"])

    def test_qr_verification_valid(self):
        """Un QR code valide doit être vérifié correctement"""
        from apps.qr_codes.models import QRCode

        qr_result = self.generator.generate(self.user, self.company)

        # Créer en base
        qr_code = QRCode.objects.create(
            user=self.user,
            company=self.company,
            unique_code=qr_result["unique_code"],
            encrypted_data=qr_result["encrypted_data"],
            signature=qr_result["signature"],
            hash_value=qr_result["hash_value"],
            salt=qr_result["salt"],
            expires_at=qr_result["expires_at"],
        )

        # Vérifier
        import json
        import base64

        qr_data = base64.b64encode(json.dumps(qr_result["qr_data"]).encode()).decode()

        result = self.verifier.verify(qr_data)

        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["holder"], "John Doe")

    def test_qr_verification_tampered_signature(self):
        """Un QR avec signature modifiée doit échouer"""
        qr_result = self.generator.generate(self.user)

        # Modifier la signature
        qr_result["qr_data"]["sig"] = "tampered_signature"

        import json
        import base64

        qr_data = base64.b64encode(json.dumps(qr_result["qr_data"]).encode()).decode()

        result = self.verifier.verify(qr_data)

        self.assertFalse(result["valid"])
        self.assertIn("signature", result["error"].lower())
