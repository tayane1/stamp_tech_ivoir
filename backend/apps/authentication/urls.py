from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("2fa/setup/", views.setup_2fa, name="setup_2fa"),
    path("2fa/verify/", views.verify_2fa_setup, name="verify_2fa_setup"),
    path("2fa/disable/", views.disable_2fa, name="disable_2fa"),
]
