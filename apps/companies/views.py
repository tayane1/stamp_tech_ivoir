from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Company, CompanyMember
from .serializers import CompanySerializer, CompanyMemberSerializer


class CompanyListCreateView(generics.ListCreateAPIView):
    """List and create companies."""

    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return companies where user is a member
        return Company.objects.filter(
            members__user=self.request.user, members__is_active=True
        ).distinct()

    def perform_create(self, serializer):
        company = serializer.save(created_by=self.request.user)
        # Add creator as owner
        CompanyMember.objects.create(
            company=company, user=self.request.user, role="owner"
        )


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a company."""

    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Company.objects.filter(
            members__user=self.request.user, members__is_active=True
        ).distinct()


class CompanyMemberListCreateView(generics.ListCreateAPIView):
    """List and create company members."""

    serializer_class = CompanyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.kwargs["company_id"]
        company = get_object_or_404(Company, id=company_id)

        # Check if user has permission to view members
        if not self._has_permission(company, ["owner", "admin"]):
            return CompanyMember.objects.none()

        return CompanyMember.objects.filter(company=company)

    def perform_create(self, serializer):
        company_id = self.kwargs["company_id"]
        company = get_object_or_404(Company, id=company_id)

        # Check if user has permission to add members
        if not self._has_permission(company, ["owner", "admin"]):
            raise permissions.PermissionDenied(
                "You don't have permission to add members."
            )

        serializer.save(company=company)

    def _has_permission(self, company, required_roles):
        """Check if user has required role in company."""
        try:
            membership = CompanyMember.objects.get(
                company=company, user=self.request.user, is_active=True
            )
            return membership.role in required_roles
        except CompanyMember.DoesNotExist:
            return False


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_companies(request):
    """Get companies for the current user."""

    memberships = CompanyMember.objects.filter(
        user=request.user, is_active=True
    ).select_related("company")

    companies = []
    for membership in memberships:
        companies.append(
            {
                "id": membership.company.id,
                "name": membership.company.name,
                "role": membership.role,
                "joined_at": membership.joined_at,
            }
        )

    return Response(companies, status=status.HTTP_200_OK)
