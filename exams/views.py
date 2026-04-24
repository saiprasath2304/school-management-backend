from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsSchoolAdmin, IsTeacherOrAdmin
from .models import Exam, Mark, ReportCard
from .serializers import ExamSerializer, MarkSerializer, BulkMarkSerializer, ReportCardSerializer


# ── Exams ─────────────────────────────────────────────────────────────────────
class ExamListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset           = Exam.objects.select_related("academic_year").all()
    serializer_class   = ExamSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields   = ["academic_year", "term", "is_active"]


class ExamDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = Exam.objects.all()
    serializer_class   = ExamSerializer
    permission_classes = [IsSchoolAdmin]


# ── Marks ─────────────────────────────────────────────────────────────────────
class MarkListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = Mark.objects.select_related(
        "exam", "student", "subject", "entered_by"
    ).all()
    serializer_class   = MarkSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields   = ["exam", "student", "subject"]

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)


class MarkDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = Mark.objects.all()
    serializer_class   = MarkSerializer
    permission_classes = [IsTeacherOrAdmin]


# ── Bulk marks entry (spreadsheet-style) ─────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def bulk_enter_marks(request):
    """
    school = require_school(request)
    POST /api/exams/marks/bulk_enter/
    Body: { exam: int, subject: int, records: [{student: int, marks_obtained: float}] }
    """
    serializer = BulkMarkSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    exam_id    = serializer.validated_data["exam"]
    subject_id = serializer.validated_data["subject"]
    records    = serializer.validated_data["records"]

    try:
        exam    = Exam.objects.get(pk=exam_id)
        from students.models import Subject
        subject = Subject.objects.get(pk=subject_id)
    except (Exam.DoesNotExist, Subject.DoesNotExist) as e:
        return Response({"error": str(e)}, status=404)

    created, updated = 0, 0
    with transaction.atomic():
        for rec in records:
            _, was_created = Mark.objects.update_or_create(
                exam=exam, subject=subject, student_id=rec["student"],
                defaults={
                    "marks_obtained": rec["marks_obtained"],
                    "entered_by":     request.user,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

    return Response(
        {"message": f"{created} created, {updated} updated."},
        status=status.HTTP_201_CREATED,
    )


# ── Class marksheet ───────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsTeacherOrAdmin])
def class_marksheet(request):
    """
    school = require_school(request)
    GET /api/exams/marks/class_marksheet/?exam=1&classroom=1
    Returns a full marksheet grid for a class for an exam.
    """
    exam_id      = request.query_params.get("exam")
    classroom_id = request.query_params.get("classroom")
    if not exam_id or not classroom_id:
        return Response({"error": "exam and classroom params required."}, status=400)

    from students.models import Student, Subject, ClassRoom
    try:
        exam      = Exam.objects.get(pk=exam_id)
        classroom = ClassRoom.objects.get(pk=classroom_id)
    except (Exam.DoesNotExist, ClassRoom.DoesNotExist) as e:
        return Response({"error": str(e)}, status=404)

    students = Student.objects.filter(current_class=classroom, is_active=True).order_by("last_name")
    subjects = Subject.objects.filter(grade=classroom.grade)
    marks    = Mark.objects.filter(exam=exam, student__current_class=classroom).select_related("subject", "student")

    # Build quick-access dict
    marks_dict = {(m.student_id, m.subject_id): m.marks_obtained for m in marks}

    grid = []
    for s in students:
        row = {
            "student_id":       s.id,
            "admission_number": s.admission_number,
            "full_name":        s.full_name,
            "marks":            {},
            "total":            0,
        }
        for sub in subjects:
            m = marks_dict.get((s.id, sub.id))
            row["marks"][sub.code] = float(m) if m is not None else None
            if m is not None:
                row["total"] += float(m)
        grid.append(row)

    return Response({
        "exam":     ExamSerializer(exam).data,
        "subjects": [{"id": sub.id, "code": sub.code, "name": sub.name} for sub in subjects],
        "grid":     grid,
    })


# ── Report Cards ──────────────────────────────────────────────────────────────
class ReportCardListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset           = ReportCard.objects.select_related("exam", "student").all()
    serializer_class   = ReportCardSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields   = ["exam", "student", "is_released"]


@api_view(["POST"])
@permission_classes([IsSchoolAdmin])
def generate_report_card(request, pk):
    """
    school = require_school(request)POST /api/exams/report-cards/<pk>/generate/ — generate PDF for a report card."""
    try:
        report_card = ReportCard.objects.select_related(
            "exam__academic_year", "student__current_class"
        ).get(pk=pk)
    except ReportCard.DoesNotExist:
        return Response({"error": "Report card not found."}, status=404)

    from utils.pdf_generator import generate_report_card_pdf
    from django.core.files.base import ContentFile

    pdf_bytes = generate_report_card_pdf(report_card)
    filename  = f"rc_{report_card.student.admission_number}_{report_card.exam.id}.pdf"
    report_card.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
    report_card.generated_at = timezone.now()
    report_card.save()

    return Response(ReportCardSerializer(report_card).data)


@api_view(["POST"])
@permission_classes([IsSchoolAdmin])
def release_report_card(request, pk):
    """
    school = require_school(request)POST /api/exams/report-cards/<pk>/release/ — make report card visible to parent."""
    try:
        report_card = ReportCard.objects.get(pk=pk)
    except ReportCard.DoesNotExist:
        return Response({"error": "Report card not found."}, status=404)

    if not report_card.pdf_file:
        return Response({"error": "Generate the PDF first before releasing."}, status=400)

    report_card.is_released = True
    report_card.released_at = timezone.now()
    report_card.save()
    return Response(ReportCardSerializer(report_card).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def download_report_card_pdf(request, pk):
    """
    school = require_school(request)GET /api/exams/report-cards/<pk>/pdf/ — download the PDF."""
    try:
        report_card = ReportCard.objects.select_related("student", "exam").get(pk=pk)
    except ReportCard.DoesNotExist:
        return Response({"error": "Not found."}, status=404)

    # Parents can only download released cards for their children
    user = request.user
    if user.role == "parent":
        if not report_card.is_released:
            return Response({"error": "Report card not yet released."}, status=403)
        if report_card.student.parent_user_id != user.id:
            return Response({"error": "Not authorised."}, status=403)

    if not report_card.pdf_file:
        return Response({"error": "PDF not generated yet."}, status=404)

    response = HttpResponse(report_card.pdf_file.read(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="report_card_{report_card.student.admission_number}.pdf"'
    )
    return response
