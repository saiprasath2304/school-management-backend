from django.db import transaction
from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from students.models import ClassRoom, Student
from accounts.permissions import IsTeacherOrAdmin, IsSchoolAdmin
from .models import AttendanceSession, AttendanceRecord
from .serializers import AttendanceSessionSerializer, BulkAttendanceSubmitSerializer


class AttendanceSessionListCreate(TenantMixin, generics.ListCreateAPIView):
    serializer_class   = AttendanceSessionSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields   = ["classroom", "date", "is_submitted"]
    ordering_fields    = ["date"]

    def get_queryset(self):
        qs = AttendanceSession.objects.select_related(
            "classroom", "submitted_by"
        ).prefetch_related("records__student")
        user = self.request.user
        # Teachers only see their own classes
        if user.is_teacher:
            qs = qs.filter(classroom__class_teacher=user)
        return qs.order_by("-date")


class AttendanceSessionDetail(TenantMixin, generics.RetrieveUpdateAPIView):
    queryset           = AttendanceSession.objects.prefetch_related("records__student")
    serializer_class   = AttendanceSessionSerializer
    permission_classes = [IsTeacherOrAdmin]


@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def bulk_submit(request):
    """
    school = require_school(request)
    POST /api/attendance/bulk_submit/
    Body: { classroom: int, date: "YYYY-MM-DD", records: [{student, status, remarks}] }
    Creates or updates an AttendanceSession + AttendanceRecords atomically.
    """
    serializer = BulkAttendanceSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    classroom_id = serializer.validated_data["classroom"]
    date         = serializer.validated_data["date"]
    records_data = serializer.validated_data["records"]

    try:
        classroom = ClassRoom.objects.get(pk=classroom_id)
    except ClassRoom.DoesNotExist:
        return Response({"error": "Classroom not found."}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        session, _ = AttendanceSession.objects.get_or_create(
            classroom=classroom,
            date=date,
            defaults={"submitted_by": request.user},
        )
        if session.is_submitted:
            return Response(
                {"error": "Attendance already submitted for this class on this date."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Upsert each record
        for rec in records_data:
            AttendanceRecord.objects.update_or_create(
                session=session,
                student_id=rec["student"].id,
                defaults={
                    "status": rec["status"],
                    "remarks": rec.get("remarks", ""),
                },
            )
        session.submitted_by = request.user
        session.is_submitted = True
        session.save()

    return Response(
        AttendanceSessionSerializer(session).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsTeacherOrAdmin])
def class_grid(request):
    """
    school = require_school(request)
    GET /api/attendance/class_grid/?classroom=1&date=2024-03-01
    Returns full attendance grid for teacher to fill in.
    """
    classroom_id = request.query_params.get("classroom")
    date         = request.query_params.get("date")
    if not classroom_id or not date:
        return Response({"error": "classroom and date params required."}, status=400)

    students = Student.objects.filter(
        current_class_id=classroom_id, is_active=True
    ).order_by("last_name", "first_name")

    try:
        session = AttendanceSession.objects.prefetch_related("records").get(
            classroom_id=classroom_id, date=date
        )
        status_map = {r.student_id: r.status for r in session.records.all()}
        is_submitted = session.is_submitted
    except AttendanceSession.DoesNotExist:
        status_map   = {}
        is_submitted = False

    grid = [
        {
            "student_id":       s.id,
            "admission_number": s.admission_number,
            "full_name":        s.full_name,
            "status":           status_map.get(s.id, "P"),
        }
        for s in students
    ]
    return Response({"date": date, "is_submitted": is_submitted, "grid": grid})


@api_view(["GET"])
@permission_classes([IsTeacherOrAdmin])
def daily_report(request):
    """
    school = require_school(request)
    GET /api/attendance/daily_report/?date=2024-03-01
    Admin view: all classes, summary counts.
    """
    date = request.query_params.get("date")
    if not date:
        return Response({"error": "date param required."}, status=400)

    sessions = AttendanceSession.objects.filter(date=date).select_related("classroom")
    report = []
    for s in sessions:
        records = s.records.all()
        report.append({
            "classroom":  str(s.classroom),
            "is_submitted": s.is_submitted,
            "present":    records.filter(status="P").count(),
            "absent":     records.filter(status="A").count(),
            "late":       records.filter(status="L").count(),
            "total":      records.count(),
        })
    return Response(report)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def student_monthly(request):
    """
    school = require_school(request)
    GET /api/attendance/student_monthly/?student=1&month=2024-03
    Returns day-wise attendance for a student in a given month.
    """
    student_id = request.query_params.get("student")
    month      = request.query_params.get("month")  # YYYY-MM
    if not student_id or not month:
        return Response({"error": "student and month params required."}, status=400)

    year, mon = month.split("-")
    records = AttendanceRecord.objects.filter(
        student_id=student_id,
        session__date__year=year,
        session__date__month=mon,
    ).select_related("session").order_by("session__date")

    total   = records.count()
    present = records.filter(status="P").count()
    absent  = records.filter(status="A").count()
    late    = records.filter(status="L").count()

    data = [
        {"date": str(r.session.date), "status": r.status}
        for r in records
    ]
    return Response({
        "student_id": student_id,
        "month":      month,
        "total_days": total,
        "present":    present,
        "absent":     absent,
        "late":       late,
        "percentage": round((present / total * 100), 1) if total else 0,
        "records":    data,
    })
