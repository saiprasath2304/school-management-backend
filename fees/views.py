from django.db.models import Sum, Q
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsSchoolAdmin, IsAccountantOrAdmin
from .models import FeeHead, FeeStructure, FeeReceipt
from .serializers import FeeHeadSerializer, FeeStructureSerializer, FeeReceiptSerializer


# ── Fee Heads ─────────────────────────────────────────────────────────────────
class FeeHeadListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset           = FeeHead.objects.all()
    serializer_class   = FeeHeadSerializer
    permission_classes = [IsAccountantOrAdmin]


class FeeHeadDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = FeeHead.objects.all()
    serializer_class   = FeeHeadSerializer
    permission_classes = [IsAccountantOrAdmin]


# ── Fee Structure ─────────────────────────────────────────────────────────────
class FeeStructureListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = FeeStructure.objects.select_related(
        "academic_year", "grade", "fee_head"
    ).all()
    serializer_class   = FeeStructureSerializer
    permission_classes = [IsAccountantOrAdmin]
    filterset_fields   = ["academic_year", "grade", "fee_head"]


class FeeStructureDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = FeeStructure.objects.all()
    serializer_class   = FeeStructureSerializer
    permission_classes = [IsAccountantOrAdmin]


# ── Receipts ──────────────────────────────────────────────────────────────────
class FeeReceiptListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = FeeReceipt.objects.select_related(
        "student", "academic_year", "fee_head", "collected_by"
    ).all()
    serializer_class   = FeeReceiptSerializer
    permission_classes = [IsAccountantOrAdmin]
    filterset_fields   = ["student", "academic_year", "fee_head", "payment_mode", "month"]
    search_fields      = ["student__admission_number", "student__first_name", "receipt_number"]
    ordering_fields    = ["payment_date", "created_at"]

    def perform_create(self, serializer):
        serializer.save(collected_by=self.request.user)


class FeeReceiptDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = FeeReceipt.objects.all()
    serializer_class   = FeeReceiptSerializer
    permission_classes = [IsAccountantOrAdmin]


# ── Receipt PDF download ───────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAccountantOrAdmin])
def download_receipt_pdf(request, pk):
    """
    school = require_school(request)GET /api/fees/receipts/<pk>/pdf/ — download the fee receipt as PDF."""
    try:
        receipt = FeeReceipt.objects.select_related(
            "student__current_class", "fee_head", "academic_year", "collected_by"
        ).get(pk=pk)
    except FeeReceipt.DoesNotExist:
        return Response({"error": "Receipt not found."}, status=404)

    from utils.pdf_generator import generate_fee_receipt_pdf
    pdf_bytes = generate_fee_receipt_pdf(receipt)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
    )
    return response


# ── Defaulter list ────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAccountantOrAdmin])
def defaulter_list(request):
    """
    school = require_school(request)
    GET /api/fees/defaulter_list/?academic_year=1&fee_head=1&month=2024-03
    Returns students who have NOT paid the given fee head for the given month.
    """
    academic_year_id = request.query_params.get("academic_year")
    fee_head_id      = request.query_params.get("fee_head")
    month            = request.query_params.get("month")

    if not academic_year_id or not fee_head_id:
        return Response({"error": "academic_year and fee_head params required."}, status=400)

    from students.models import Student
    all_students = Student.objects.filter(is_active=True).select_related("current_class")

    paid_filter = Q(
        fee_receipts__academic_year_id=academic_year_id,
        fee_receipts__fee_head_id=fee_head_id,
    )
    if month:
        paid_filter &= Q(fee_receipts__month=month)

    paid_ids = Student.objects.filter(paid_filter).values_list("id", flat=True)
    defaulters = all_students.exclude(id__in=paid_ids)

    data = [
        {
            "student_id":       s.id,
            "admission_number": s.admission_number,
            "full_name":        s.full_name,
            "class":            str(s.current_class) if s.current_class else "—",
            "parent_phone":     s.parent_phone,
        }
        for s in defaulters
    ]
    return Response({"count": len(data), "defaulters": data})


# ── Student balance ───────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def student_balance(request):
    """
    school = require_school(request)
    GET /api/fees/student_balance/?student=1&academic_year=1
    Returns paid receipts and total paid for a student.
    """
    student_id       = request.query_params.get("student")
    academic_year_id = request.query_params.get("academic_year")

    if not student_id or not academic_year_id:
        return Response({"error": "student and academic_year params required."}, status=400)

    receipts = FeeReceipt.objects.filter(
        student_id=student_id,
        academic_year_id=academic_year_id,
    ).select_related("fee_head").order_by("payment_date")

    total_paid = receipts.aggregate(total=Sum("amount_paid"))["total"] or 0

    data = FeeReceiptSerializer(receipts, many=True).data
    return Response({
        "student_id":    student_id,
        "academic_year": academic_year_id,
        "total_paid":    total_paid,
        "receipts":      data,
    })
