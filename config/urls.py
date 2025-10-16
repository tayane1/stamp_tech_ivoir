"""
URL configuration for stamp project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="STAMP TECH IVOIRE API",
        default_version="v1",
        description="API de gestion des QR codes sécurisés",
        terms_of_service="https://www.stamptech.ci/terms/",
        contact=openapi.Contact(email="contact@stamptech.ci"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="api-redoc"),
    # API Endpoints
    path("api/auth/", include("apps.authentication.urls")),
    path("api/qr-codes/", include("apps.qr_codes.urls")),
    path("api/companies/", include("apps.companies.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personnalisation Admin
admin.site.site_header = "STAMP TECH IVOIRE Admin"
admin.site.site_title = "STAMP TECH"
admin.site.index_title = "Gestion de la plateforme"
