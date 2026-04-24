"""
tenants/middleware.py
─────────────────────────────────────────────────────────────────
Resolves the current School (tenant) on every HTTP request.

Resolution order:
  1. Subdomain  → greenfield.eduverse.com  (__production__)
  2. X-School-ID header                    (__development/testing__)
  3. X-School-Subdomain header             (__development/testing__)

Sets  request.school = School instance | None
"""
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.school = self._resolve(request)

    @staticmethod
    def _resolve(request):
        from tenants.models import School

        # ── 1. Subdomain detection ──────────────────────────────────
        host   = request.get_host().split(":")[0]   # strip port
        parts  = host.split(".")

        # Expect at least  subdomain.domain.tld  (3 parts)
        # but skip known non-tenant subdomains
        if len(parts) >= 3 and parts[0] not in ("www", "api", "admin", "mail"):
            try:
                return School.objects.get(subdomain=parts[0], is_active=True)
            except School.DoesNotExist:
                pass

        # ── 2. X-School-ID header (dev / Flutter local testing) ────
        school_id = request.headers.get("X-School-ID")
        if school_id:
            try:
                return School.objects.get(pk=int(school_id), is_active=True)
            except (School.DoesNotExist, ValueError):
                pass

        # ── 3. X-School-Subdomain header (dev alternative) ─────────
        subdomain = request.headers.get("X-School-Subdomain")
        if subdomain:
            try:
                return School.objects.get(subdomain=subdomain, is_active=True)
            except School.DoesNotExist:
                pass

        return None
