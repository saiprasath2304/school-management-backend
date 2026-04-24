from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsSchoolAdmin
from .models import School
from .serializers import SchoolSerializer, SchoolRegisterSerializer


class SchoolRegisterView(generics.CreateAPIView):
    """
    POST /api/public/schools/register/
    Public endpoint — no auth required.
    Creates a new School tenant + first admin user.
    30-day free trial starts immediately.
    """
    queryset           = School.objects.all()
    serializer_class   = SchoolRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school = serializer.save()
        return Response(
            {
                "message": f"✅ School '{school.name}' registered successfully!",
                "subdomain": school.subdomain,
                "login_url": f"https://{school.subdomain}.eduverse.com/api/token/",
                "admin_panel": f"https://{school.subdomain}.eduverse.com/admin/",
                "trial_ends_at": str(school.trial_ends_at),
                "school": SchoolSerializer(school).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SchoolDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/tenants/school/  — get current school settings
    PATCH /api/tenants/school/ — update school settings (admin only)
    """
    serializer_class   = SchoolSerializer
    permission_classes = [IsSchoolAdmin]

    def get_object(self):
        school = getattr(self.request, "school", None)
        if not school:
            from rest_framework.exceptions import NotFound
            raise NotFound("School not found.")
        return school


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def check_subdomain(request):
    """
    GET /api/public/check-subdomain/?subdomain=greenfield
    Check if a subdomain is available before registering.
    """
    subdomain = request.query_params.get("subdomain", "").strip().lower()
    if not subdomain:
        return Response({"error": "subdomain param required."}, status=400)
    taken = School.objects.filter(subdomain=subdomain).exists()
    return Response({
        "subdomain": subdomain,
        "available": not taken,
    })
