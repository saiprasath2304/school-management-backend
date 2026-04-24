from django.urls import path
from .views import SchoolRegisterView, SchoolDetailView, check_subdomain

urlpatterns = [
    # ── Public (no auth) ─────────────────────────────────────────
    path("public/schools/register/",   SchoolRegisterView.as_view(), name="school-register"),
    path("public/check-subdomain/",    check_subdomain,               name="check-subdomain"),

    # ── Tenant-scoped (auth required) ────────────────────────────
    path("tenants/school/",            SchoolDetailView.as_view(),    name="school-detail"),
]
