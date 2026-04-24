from django.utils import timezone
from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsSchoolAdmin, IsTeacherOrAdmin
from .models import Notice, TimetableSlot
from .serializers import NoticeSerializer, TimetableSlotSerializer


# ── Notices ───────────────────────────────────────────────────────────────────
class NoticeListCreate(TenantMixin, generics.ListCreateAPIView):
    serializer_class = NoticeSerializer
    filterset_fields = ["is_published", "priority", "target_grade"]

    def get_queryset(self):
        user = self.request.user
        qs   = Notice.objects.select_related("published_by", "target_grade")
        # Parents/students only see published, non-expired notices
        if user.role in ("parent", "student"):
            today = timezone.now().date()
            qs = qs.filter(is_published=True).filter(
                models_or_null_expires(today)
            )
        return qs.order_by("-created_at")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSchoolAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(published_by=self.request.user)


def models_or_null_expires(today):
    """Helper: expires_at is null OR in the future."""
    from django.db.models import Q
    return Q(expires_at__isnull=True) | Q(expires_at__gte=today)


class NoticeDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = Notice.objects.all()
    serializer_class   = NoticeSerializer
    permission_classes = [IsSchoolAdmin]


@api_view(["POST"])
@permission_classes([IsSchoolAdmin])
def publish_notice(request, pk):
    """
    school = require_school(request)POST /api/portal/notices/<pk>/publish/"""
    try:
        notice = Notice.objects.get(pk=pk)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found."}, status=404)
    notice.is_published = True
    notice.save()
    return Response(NoticeSerializer(notice).data)


# ── Timetable ─────────────────────────────────────────────────────────────────
class TimetableListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = TimetableSlot.objects.select_related(
        "classroom", "subject", "teacher"
    ).all()
    serializer_class = TimetableSlotSerializer
    filterset_fields = ["classroom", "day", "is_published", "teacher"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSchoolAdmin()]
        return [permissions.IsAuthenticated()]


class TimetableDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = TimetableSlot.objects.all()
    serializer_class   = TimetableSlotSerializer
    permission_classes = [IsSchoolAdmin]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def timetable_for_class(request):
    """
    school = require_school(request)
    GET /api/portal/timetable/for_class/?classroom=1
    Public timetable view for parents/students — only published slots.
    """
    classroom_id = request.query_params.get("classroom")
    if not classroom_id:
        return Response({"error": "classroom param required."}, status=400)

    slots = TimetableSlot.objects.filter(
        classroom_id=classroom_id, is_published=True
    ).select_related("subject", "teacher").order_by("day", "slot_number")

    # Organise into a week dict
    week = {day: [] for day in range(1, 7)}
    for slot in slots:
        week[slot.day].append(TimetableSlotSerializer(slot).data)

    return Response({
        "classroom_id": classroom_id,
        "timetable":    week,
    })


@api_view(["POST"])
@permission_classes([IsSchoolAdmin])
def publish_class_timetable(request):
    """
    school = require_school(request)
    POST /api/portal/timetable/publish_class/
    Body: { classroom: int }
    Marks all slots for the class as published.
    """
    classroom_id = request.data.get("classroom")
    if not classroom_id:
        return Response({"error": "classroom required."}, status=400)

    updated = TimetableSlot.objects.filter(
        classroom_id=classroom_id
    ).update(is_published=True)
    return Response({"published_slots": updated})


# ── Parent / Student Dashboard ────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_dashboard(request):
    """
    school = require_school(request)
    GET /api/portal/dashboard/
    Returns a combined dashboard payload for the logged-in parent/student.
    """
    user = request.user
    if user.role not in ("parent", "student"):
        return Response({"error": "Only parents and students have a dashboard."}, status=403)

    from students.models import Student
    from attendance.models import AttendanceRecord
    from fees.models import FeeReceipt
    from exams.models import ReportCard

    # Get the student(s) linked to this parent
    if user.role == "parent":
        students = Student.objects.filter(parent_user=user, is_active=True)
    else:
        students = Student.objects.filter(parent_user=user, is_active=True)  # Same for student login

    result = []
    today  = timezone.now().date()

    for student in students:
        # -- Attendance this month
        month_records = AttendanceRecord.objects.filter(
            student=student,
            session__date__year=today.year,
            session__date__month=today.month,
        )
        total   = month_records.count()
        present = month_records.filter(status="P").count()

        # -- Recently released report cards
        report_cards = ReportCard.objects.filter(
            student=student, is_released=True
        ).select_related("exam").order_by("-released_at")[:3]

        # -- Pending fee dues (last 3 receipts)
        recent_receipts = FeeReceipt.objects.filter(
            student=student
        ).select_related("fee_head").order_by("-payment_date")[:5]

        # -- Current timetable class
        classroom = student.current_class

        result.append({
            "student": {
                "id":               student.id,
                "full_name":        student.full_name,
                "admission_number": student.admission_number,
                "class":            str(classroom) if classroom else "—",
            },
            "attendance": {
                "month":      f"{today.year}-{today.month:02d}",
                "total_days": total,
                "present":    present,
                "percentage": round(present / total * 100, 1) if total else 0,
            },
            "report_cards": [
                {
                    "id":          rc.id,
                    "exam":        str(rc.exam),
                    "released_at": str(rc.released_at),
                }
                for rc in report_cards
            ],
            "recent_payments": [
                {
                    "receipt_number": r.receipt_number,
                    "fee_head":       r.fee_head.name,
                    "amount":         float(r.amount_paid),
                    "date":           str(r.payment_date),
                }
                for r in recent_receipts
            ],
        })

    # Published notices (top 5)
    notices = Notice.objects.filter(is_published=True).order_by("-created_at")[:5]

    return Response({
        "students": result,
        "notices": NoticeSerializer(notices, many=True).data,
    })
