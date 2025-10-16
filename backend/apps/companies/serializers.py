from rest_framework import serializers
from .models import Company, CompanyMember


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "description",
            "website",
            "email",
            "phone",
            "address",
            "logo",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CompanyMemberSerializer(serializers.ModelSerializer):
    """Serializer for CompanyMember model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = CompanyMember
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "role",
            "is_active",
            "joined_at",
        ]
        read_only_fields = ["id", "joined_at"]
