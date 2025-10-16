from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.qr_codes.models import QRCode

User = get_user_model()


class QRCodeAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_qr_code(self):
        """Test création QR via API"""
        data = {"company": None}

        response = self.client.post("/api/qr-codes/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("unique_code", response.data)
        self.assertTrue(QRCode.objects.filter(user=self.user).exists())

    def test_list_qr_codes(self):
        """Test listage QR codes"""
        # Créer quelques QR
        QRCode.objects.create(
            user=self.user,
            unique_code="ST-CI-2024-TEST1",
            encrypted_data="test",
            signature="test",
            hash_value="test",
            salt="test",
        )

        response = self.client.get("/api/qr-codes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_revoke_qr_code(self):
        """Test révocation QR"""
        qr = QRCode.objects.create(
            user=self.user,
            unique_code="ST-CI-2024-TEST2",
            encrypted_data="test",
            signature="test",
            hash_value="test",
            salt="test",
        )

        response = self.client.post(f"/api/qr-codes/{qr.id}/revoke/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        qr.refresh_from_db()
        self.assertEqual(qr.status, QRCode.Status.REVOKED)

    def test_statistics(self):
        """Test endpoint statistiques"""
        response = self.client.get("/api/qr-codes/statistics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total", response.data)
        self.assertIn("active", response.data)
