from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path("admin/", admin.site.urls),

    # ── Auth ──────────────────────────────────────────────────────
    path("api/token/",           TokenObtainPairView.as_view(),   name="token_obtain_pair"),
    path("api/token/refresh/",   TokenRefreshView.as_view(),      name="token_refresh"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(),    name="token_blacklist"),

    # ── Multi-tenant public + tenant endpoints ────────────────────
    path("api/", include("tenants.urls")),

    # ── App APIs ──────────────────────────────────────────────────
    path("api/accounts/",  include("accounts.urls")),
    path("api/students/",  include("students.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/fees/",      include("fees.urls")),
    path("api/exams/",     include("exams.urls")),
    path("api/hr/",        include("hr.urls")),
    path("api/library/",   include("library.urls")),
    path("api/portal/",    include("portal.urls")),

    # ── API Docs ──────────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/",   SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
