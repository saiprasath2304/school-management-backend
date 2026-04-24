from rest_framework import generics, permissions
from tenants.mixins import TenantMixin, require_school
from django_filters.rest_framework import DjangoFilterBackend
from .models import AcademicYear, Grade, ClassRoom, Student, Subject, StaffProfile
from .serializers import (
    AcademicYearSerializer, GradeSerializer, ClassRoomSerializer,
    StudentSerializer, SubjectSerializer, StaffProfileSerializer,
)
from accounts.permissions import IsSchoolAdmin, IsTeacherOrAdmin


# ── Academic Year ─────────────────────────────────────────────────────────────
class AcademicYearListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset         = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsSchoolAdmin]


class AcademicYearDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsSchoolAdmin]


# ── Grades ────────────────────────────────────────────────────────────────────
class GradeListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset         = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsTeacherOrAdmin]


class GradeDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsSchoolAdmin]


# ── Subjects ──────────────────────────────────────────────────────────────────
class SubjectListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset         = Subject.objects.select_related("grade").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields  = ["grade"]


class SubjectDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsSchoolAdmin]


# ── ClassRooms ────────────────────────────────────────────────────────────────
class ClassRoomListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = ClassRoom.objects.select_related(
        "grade", "academic_year", "class_teacher"
    ).all()
    serializer_class   = ClassRoomSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields   = ["grade", "academic_year", "class_teacher"]


class ClassRoomDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsSchoolAdmin]


# ── Students ──────────────────────────────────────────────────────────────────
class StudentListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = Student.objects.select_related("current_class", "parent_user").all()
    serializer_class   = StudentSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields   = ["current_class", "is_active", "gender"]
    search_fields      = ["first_name", "last_name", "admission_number", "parent_phone"]
    ordering_fields    = ["admission_number", "last_name"]


class StudentDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrAdmin]


# ── Staff ─────────────────────────────────────────────────────────────────────
class StaffListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = StaffProfile.objects.select_related("user").prefetch_related("subjects_taught").all()
    serializer_class   = StaffProfileSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields   = ["department", "is_active"]
    search_fields      = ["employee_id", "user__first_name", "user__last_name"]


class StaffDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset         = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsSchoolAdmin]
