from rest_framework import serializers
from .models import QRCode, QRVerification


class QRCodeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "id",
            "unique_code",
            "status",
            "company",
            "company_name",
            "created_at",
            "expires_at",
            "last_verified_at",
            "is_valid",
        ]
        read_only_fields = ["id", "unique_code", "created_at"]

    def get_is_valid(self, obj):
        return obj.is_valid()


class QRVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRVerification
        fields = "__all__"
