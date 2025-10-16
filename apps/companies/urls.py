from django.urls import path
from . import views

app_name = "companies"

urlpatterns = [
    path("", views.CompanyListCreateView.as_view(), name="company-list-create"),
    path("<int:pk>/", views.CompanyDetailView.as_view(), name="company-detail"),
    path(
        "<int:company_id>/members/",
        views.CompanyMemberListCreateView.as_view(),
        name="member-list-create",
    ),
    path("user-companies/", views.user_companies, name="user-companies"),
]
