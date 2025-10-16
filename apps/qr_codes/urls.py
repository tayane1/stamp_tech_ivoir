from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "qr_codes"

router = DefaultRouter()
router.register(r"", views.QRCodeViewSet, basename="qr-codes")
router.register(r"verify", views.QRVerificationView, basename="qr-verification")

urlpatterns = [
    path("", include(router.urls)),
]
