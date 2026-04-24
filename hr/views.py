from django.utils import timezone
from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsSchoolAdmin, IsHROrAdmin
from .models import LeaveType, LeaveApplication, Payroll
from .serializers import LeaveTypeSerializer, LeaveApplicationSerializer, PayrollSerializer


# ── Leave Types ───────────────────────────────────────────────────────────────
class LeaveTypeListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset           = LeaveType.objects.all()
    serializer_class   = LeaveTypeSerializer
    permission_classes = [IsHROrAdmin]


class LeaveTypeDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = LeaveType.objects.all()
    serializer_class   = LeaveTypeSerializer
    permission_classes = [IsHROrAdmin]


# ── Leave Applications ────────────────────────────────────────────────────────
class LeaveApplicationListCreate(TenantMixin, generics.ListCreateAPIView):
    serializer_class   = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields   = ["status", "leave_type", "staff"]

    def get_queryset(self):
        qs   = LeaveApplication.objects.select_related("staff__user", "leave_type", "reviewed_by")
        user = self.request.user
        # Staff can only see their own applications
        if not (user.is_school_admin or user.role in ("hr_admin",)):
            return qs.filter(staff__user=user)
        return qs.order_by("-applied_on")

    def perform_create(self, serializer):
        from students.models import StaffProfile
        try:
            staff = StaffProfile.objects.get(user=self.request.user)
        except StaffProfile.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You do not have a staff profile.")
        serializer.save(staff=staff)


class LeaveApplicationDetail(TenantMixin, generics.RetrieveUpdateAPIView):
    queryset           = LeaveApplication.objects.all()
    serializer_class   = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([IsHROrAdmin])
def approve_leave(request, pk):
    """
    school = require_school(request)POST /api/hr/leaves/<pk>/approve/"""
    try:
        leave = LeaveApplication.objects.get(pk=pk)
    except LeaveApplication.DoesNotExist:
        return Response({"error": "Leave application not found."}, status=404)

    if leave.status != "pending":
        return Response({"error": f"Leave is already {leave.status}."}, status=400)

    leave.status       = "approved"
    leave.reviewed_by  = request.user
    leave.reviewed_on  = timezone.now()
    leave.admin_remarks = request.data.get("admin_remarks", "")
    leave.save()
    return Response(LeaveApplicationSerializer(leave).data)


@api_view(["POST"])
@permission_classes([IsHROrAdmin])
def reject_leave(request, pk):
    """
    school = require_school(request)POST /api/hr/leaves/<pk>/reject/"""
    try:
        leave = LeaveApplication.objects.get(pk=pk)
    except LeaveApplication.DoesNotExist:
        return Response({"error": "Leave application not found."}, status=404)

    if leave.status != "pending":
        return Response({"error": f"Leave is already {leave.status}."}, status=400)

    leave.status        = "rejected"
    leave.reviewed_by   = request.user
    leave.reviewed_on   = timezone.now()
    leave.admin_remarks = request.data.get("admin_remarks", "")
    leave.save()
    return Response(LeaveApplicationSerializer(leave).data)


# ── Payroll ───────────────────────────────────────────────────────────────────
class PayrollListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = Payroll.objects.select_related("staff__user", "created_by").all()
    serializer_class   = PayrollSerializer
    permission_classes = [IsHROrAdmin]
    filterset_fields   = ["staff", "month", "status"]
    search_fields      = ["staff__employee_id", "staff__user__first_name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PayrollDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = Payroll.objects.all()
    serializer_class   = PayrollSerializer
    permission_classes = [IsHROrAdmin]


@api_view(["POST"])
@permission_classes([IsHROrAdmin])
def process_payroll_month(request):
    """
    school = require_school(request)
    POST /api/hr/salaries/process/
    Body: { month: "2024-03" }
    Auto-generates draft payroll for ALL active staff, incorporating
    any approved unpaid leave (loss of pay) automatically.
    """
    month = request.data.get("month")
    if not month:
        return Response({"error": "month (YYYY-MM) required."}, status=400)

    from students.models import StaffProfile
    from django.db.models import Q

    staff_list = StaffProfile.objects.filter(is_active=True).select_related("user")
    created, skipped = 0, 0

    for staff in staff_list:
        if Payroll.objects.filter(staff=staff, month=month).exists():
            skipped += 1
            continue

        # Sum approved leave days (unpaid) in this month
        year, mon = month.split("-")
        unpaid_days = 0
        approved_leaves = LeaveApplication.objects.filter(
            staff=staff,
            status="approved",
            leave_type__is_paid=False,
            from_date__year=year,
            from_date__month=mon,
        )
        for leave in approved_leaves:
            unpaid_days += leave.total_days

        per_day   = float(staff.base_salary) / 26  # working days
        lop_amt   = round(per_day * unpaid_days, 2)
        net       = float(staff.base_salary) - lop_amt

        Payroll.objects.create(
            staff=staff,
            month=month,
            base_salary=staff.base_salary,
            allowances=0,
            deductions=0,
            loss_of_pay_days=unpaid_days,
            loss_of_pay_amount=lop_amt,
            net_salary=net,
            status="draft",
            created_by=request.user,
        )
        created += 1

    return Response({"created": created, "skipped": skipped})


@api_view(["POST"])
@permission_classes([IsHROrAdmin])
def mark_payroll_paid(request, pk):
    """
    school = require_school(request)POST /api/hr/salaries/<pk>/mark_paid/"""
    try:
        payroll = Payroll.objects.get(pk=pk)
    except Payroll.DoesNotExist:
        return Response({"error": "Payroll record not found."}, status=404)

    payroll.status            = "paid"
    payroll.payment_date      = request.data.get("payment_date")
    payroll.payment_reference = request.data.get("payment_reference", "")
    payroll.save()
    return Response(PayrollSerializer(payroll).data)
