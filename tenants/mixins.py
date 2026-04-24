"""
tenants/mixins.py
─────────────────────────────────────────────────────────────────
Drop-in mixins for class-based views to enforce tenant isolation.

Usage (class-based):
    class StudentListCreate(TenantMixin, generics.ListCreateAPIView):
        ...

Usage (function-based):  use  require_school(request)  helper.
"""
from rest_framework.exceptions import PermissionDenied


def require_school(request):
    """Raise PermissionDenied if no school is resolved on the request."""
    if not getattr(request, "school", None):
        raise PermissionDenied(
            "No school context detected. "
            "Use the correct subdomain or include X-School-ID / X-School-Subdomain header."
        )
    return request.school


class TenantMixin:
    """
    Automatically:
    1. Filters get_queryset() to the current tenant's rows.
    2. Injects school into perform_create() saves.
    3. Raises PermissionDenied if no school is resolved.
    """

    def _school(self):
        return require_school(self.request)

    def get_queryset(self):
        school = self._school()
        return super().get_queryset().filter(school=school)

    def perform_create(self, serializer):
        serializer.save(school=self._school())
